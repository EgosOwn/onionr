from secrets import randbits
import base64

from typing import Union

import ujson
from onionrblocks import Block
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


# As per dandelion++ spec the edge should be the same.
# We keep it the same for each daemon life time.
queue_to_use = randbits(1)


@dispatcher.add_method
def insert_block(block: Union[dict, Block]):
    if isinstance(block, dict):
        block = Block(
            block['id'], base64.b64decode(block['raw']), auto_verify=False)
    gossip_block_queues[queue_to_use].put_nowait(block)
    return "ok"
