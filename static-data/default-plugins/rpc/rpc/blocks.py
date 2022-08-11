from secrets import randbits

from onionrblocks import Block
from jsonrpc import dispatcher
import ujson
from base64 import b85decode

from gossip.blockqueues import gossip_block_queues
from blockdb import get_blocks_after_timestamp


@dispatcher.add_method
def get_blocks(timestamp):
    return [block.raw for block in get_blocks_after_timestamp(timestamp)]


queue_to_use = randbits(1)
@dispatcher.add_method
def insert_block(block):
    block = Block(
        block['id'], b85decode(block['raw']), auto_verify=False)
    gossip_block_queues[queue_to_use].put_nowait(block)
    return "ok"

#dispatcher['get_blocks_after_timestamp'] = get_blocks_after_timestamp
