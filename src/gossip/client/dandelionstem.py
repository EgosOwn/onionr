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
    # Deep copy the block queues so that everything gets
    # stemmed out if we run out of time in epoch
    # Also spawn a thread with block set to add to db after time for black hole attack
    block = block_queue.get(block=True, timeout=d_phase.remaining_time)
    raw_block = block.raw
    block_size = len(block.raw)
    block_id = block.id
    del block

