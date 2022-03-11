from queue import Queue
from time import sleep

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ordered_set import OrderedSet
    from onionrblocks import Block
    from ..peer import Peer
    from ..dandelion.phase import DandelionPhase

def stem_out(
        block_queues: Tuple[Queue['Block']],
        peer_set: OrderedSet['Peer'],
        d_phase: 'DandelionPhase'):

    # Spawn a thread with block set to add to db after time for black hole attack

    if not len(peer_set):
        sleep(1)
        return


