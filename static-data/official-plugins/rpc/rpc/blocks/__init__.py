from secrets import randbits
import base64
from time import time

from typing import Union

from onionrblocks import Block
import kasten
from kasten.generator import pack as kasten_pack

import onionrblocks
from jsonrpc import dispatcher

from gossip.blockqueues import gossip_block_queues
import blockdb
from utils import multiproc


@dispatcher.add_method
def get_block(block_id: str) -> dict:
    bl = blockdb.get_block(block_id)
    


@dispatcher.add_method
def get_blocks(timestamp):
    blocks = []
    for block in blockdb.get_blocks_after_timestamp(timestamp):
        blocks.append({
            'id': block.id,
            'raw': base64.b64encode(block.raw).decode('utf-8')
        })
    return blocks


def _do_create_block(
        block_data: 'base64', block_type: str, ttl: int, metadata: dict):
    # Wrapper for onionrblocks.create_block
    # (take base64 to be compatible with RPC)
    bl: Block = multiproc.subprocess_compute(
        onionrblocks.create_anonvdf_block,
        3600,
        base64.b64decode(block_data),
        block_type,
        ttl,
        **metadata
        )
    try:
        block_id = bl.id.decode('utf-8')
    except AttributeError:
        block_id = bl.id
    bl_json = {
        'id': block_id,
        'raw': base64.b64encode(bl.raw).decode('utf-8')
    }
    return bl_json

@dispatcher.add_method
def create_block(
        block_data: 'base64', block_type: str, ttl: int, metadata: dict):
    return _do_create_block(block_data, block_type, ttl, metadata)


@dispatcher.add_method
def create_and_insert_block(
        block_data: 'base64',
        block_type: str, ttl: int, metadata: dict) -> str:
    bl = _do_create_block(block_data, block_type, ttl, metadata)
    insert_block(bl)
    return bl


@dispatcher.add_method
def prepare_block_for_vdf(block_data: 'base64', block_type, ttl: int, metadata: dict):
    # This allows for untrusted clients to create blocks, they just have to compute the VDF
    metadata['ttl'] = ttl
    block_data = base64.b64decode(block_data)
    kasten_packed = kasten_pack.pack(block_data, block_type, metadata, int(time()))
    kasten_obj = kasten.Kasten('', kasten_packed, kasten.generator.KastenBaseGenerator, auto_check_generator=False)
    return {
        'raw': base64.b64encode(kasten_packed).decode('utf-8'),
        'rounds_needed': onionrblocks.blockcreator.anonvdf.AnonVDFGenerator.get_rounds_for_ttl_seconds(ttl, len(kasten_obj.get_packed()))
    }

@dispatcher.add_method
def assemble_and_insert_block(
        kasten_packed: 'base64', vdf_result: str) -> str:
    bl = onionrblocks.Block(
        vdf_result, 
        base64.b64decode(kasten_packed), auto_verify=True)
    insert_block(bl)
    return {
        'id': bl.id,
        'raw': base64.b64encode(bl.raw).decode('utf-8')
    }


# As per dandelion++ spec the edge should be the same.
# We keep it the same for each daemon life time.
queue_to_use = randbits(1)


@dispatcher.add_method
def insert_block(block: Union[dict, Block]):
    # Accepts dict because json and accepts block because other functions use it
    if isinstance(block, dict):
        block = Block(
            block['id'], base64.b64decode(block['raw']), auto_verify=True)
    gossip_block_queues[queue_to_use].put_nowait(block)
    return "ok"
