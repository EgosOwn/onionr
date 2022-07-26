from secrets import SystemRandom
from time import time
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from onionrblocks import Block

from gossip.commands import GossipCommands, command_to_byte
from blockdb import get_blocks_after_timestamp
from ...constants import BLOCK_ID_SIZE, BLOCK_SIZE_LEN

from ...peerset import gossip_peer_set
from ...server import lastincoming

SECS_ELAPSED_NO_INCOMING_BEFORE_STREAM = 3

class SendTimestamp:
    timestamp: int = 0

def stream_to_peer():
    if SECS_ELAPSED_NO_INCOMING_BEFORE_STREAM > time() - lastincoming.last_incoming_timestamp:
        SendTimestamp.timestamp = int(time())
        return
    if not len(gossip_peer_set):
        return 
    rand = SystemRandom()
    peer = rand.choice(gossip_peer_set)
    buffer: List['Block'] = []

    def _do_upload():
        with peer.get_socket(30) as p:
            p.sendall(command_to_byte(GossipCommands.PUT_BLOCK_DIFFUSE))

            while len(buffer):
                try:
                    block = buffer.pop()
                except IndexError:
                    break
                p.sendall(block.id.zfill(BLOCK_ID_SIZE))
                if int.from_bytes(p.recv(1), 'big') == 0:
                    continue
                block_size = str(len(block.raw)).zfill(BLOCK_SIZE_LEN)
                p.sendall(block_size.encode('utf-8'))
                p.sendall(block.raw)

    # Buffer some blocks so we're not streaming too many to one peer
    # and to efficiently avoid connecting without sending anything
    buffer_max = 10
    for block in get_blocks_after_timestamp(SendTimestamp.timestamp):
        buffer.append(block)
        if len(buffer) > buffer_max:
            _do_upload(buffer)
    if len(buffer):
        _do_upload()

    SendTimestamp.timestamp = int(time())
