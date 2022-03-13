from queue import Queue
from threading import Timer
from time import sleep
from secrets import choice
import traceback

from typing import TYPE_CHECKING, Tuple, List, Set

from onionrthreads import add_delayed_thread
from blockdb import add_block_to_db
import logger

from ..constants import BLACKHOLE_EVADE_TIMER_SECS, MAX_OUTBOUND_DANDELION_EDGE

if TYPE_CHECKING:
    from ordered_set import OrderedSet
    from onionrblocks import Block
    from ..peer import Peer
    from ..dandelion.phase import DandelionPhase


class NotEnoughEdges(ValueError): pass  # noqa


def _setup_edge(
        peer_set: OrderedSet['Peer'], exclude_set: OrderedSet['Peer']):
    """Negotiate stem connection with random peer, add to exclude set if fail"""
    try:
        peer: 'Peer' = choice(peer_set - exclude_set)
    except IndexError:
        raise NotEnoughEdges
    try:
        s = peer.get_socket()
    except Exception:
        logger.debug(traceback.format_exc())
        exclude_set.add(peer)



def stem_out(
        block_queues: Tuple[Queue['Block'], Queue['Block']],
        peer_set: OrderedSet['Peer'],
        d_phase: 'DandelionPhase'):

    # Spawn threads with deep copied block queue to add to db after time
    # for black hole attack
    for block_q in block_queues:
        add_delayed_thread(
            lambda q: set(map(add_block_to_db, q)),
            BLACKHOLE_EVADE_TIMER_SECS, list(block_q.queue))

    # don't bother if there are no possible outbound edges
    if not len(peer_set):
        sleep(1)
        return

    # Pick edges randomly
    # Using orderedset for the tried edges to ensure random pairing with queue
    tried_edges: OrderedSet['Peer'] = OrderedSet()



