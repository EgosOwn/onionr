from secrets import randbits
import base64
from base64 import b85decode

from onionrblocks import Block
import onionrblocks
from jsonrpc import dispatcher
import ujson

from gossip.blockqueues import gossip_block_queues
from blockdb import get_blocks_after_timestamp


@dispatcher.add_method
def get_blocks(timestamp):
    return [block.raw for block in get_blocks_after_timestamp(timestamp)]


@dispatcher.add_method
def create_block(
        block_data: 'base64', block_type: str, ttl: int, metadata: dict):
    # TODO use a module from an old version to use multiprocessing to avoid blocking GIL
    # Wrapper for onionrblocks.create_block (take base64 to be compatible with RPC)
    bl = onionrblocks.create_anonvdf_block(
        base64.b64decode(block_data), block_type, ttl, **metadata)
    return base64.b85encode(bl.raw).decode('utf-8')

queue_to_use = randbits(1)
@dispatcher.add_method
def insert_block(block):
    block = Block(
        block['id'], b85decode(block['raw']), auto_verify=False)
    gossip_block_queues[queue_to_use].put_nowait(block)
    return "ok"

