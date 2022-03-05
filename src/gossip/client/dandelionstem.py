from queue import Queue


from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from onionrblocks import Block
    from ..peer import Peer
    from ..dandelion.phase import DandelionPhase

def stem_out(
        block_queue: Queue['Block'],
        peer_set: Set['Block'],
        d_phase: 'DandelionPhase'):
    block = block_queue.get(block=True, timeout=5)
    raw_block = block.raw
    block_size = len(block.raw)
    block_id = block.id
    del block

