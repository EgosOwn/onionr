from queue import Queue
from threading import Thread, Timer
from time import sleep
from secrets import choice
import traceback

from typing import TYPE_CHECKING, Tuple, List, Set

from onionrthreads import add_delayed_thread
from blockdb import add_block_to_db
import logger

from ..constants import BLACKHOLE_EVADE_TIMER_SECS, MAX_OUTBOUND_DANDELION_EDGE
from ..commands import GossipCommands, command_to_byte
from .. import dandelion

if TYPE_CHECKING:
    from ordered_set import OrderedSet
    from onionrblocks import Block
    from ..peer import Peer
    from ..dandelion.phase import DandelionPhase
    import socket


class NotEnoughEdges(ValueError): pass  # noqa
class StemConnectionDenied(ConnectionRefusedError): pass  # noqa


async def _setup_edge(
        peer_set: OrderedSet['Peer'], exclude_set: OrderedSet['Peer']):
    """Negotiate stem connection with random peer, add to exclu set if fail"""
    try:
        peer: 'Peer' = choice(peer_set - exclude_set)
    except IndexError:
        raise NotEnoughEdges
    try:
        s = peer.get_socket()
    except Exception:
        logger.debug(traceback.format_exc())
        exclude_set.add(peer)

    try:
        s.sendall(command_to_byte(GossipCommands.PUT_BLOCKS))
        if s.recv(1) == dandelion.StemAcceptResult.DENY:
            raise StemConnectionDenied
    except StemConnectionDenied:
        logger.debug(
            "Stem connection denied (peer has too many) " +
            f"{peer.transport_address}")
    except Exception:
        logger.warn(
            "Error asking peer to establish stem connection" +
            traceback.format_exc(), terminal=True)
    else:
        # Return peer socket if it is in stem reception mode successfully
        return s
    finally:
        # If peer is good or bad, exclude it no matter what
        exclude_set.add(peer)
    # If they won't accept stem blocks, close the socket
    s.close()


async def _do_stem_stream(
        peer_socket: 'socket.socket',
        block_queue: Queue['Block'],
        d_phase: 'DandelionPhase'):
    return


async def stem_out(
        block_queues: Tuple[Queue['Block'], Queue['Block']],
        peer_set: OrderedSet['Peer'],
        d_phase: 'DandelionPhase'):


    # don't bother if there are no possible outbound edges
    if not len(peer_set):
        sleep(1)
        return

    # Spawn threads with deep copied block queue to add to db after time
    # for black hole attack
    for block_q in block_queues:
        add_delayed_thread(
            lambda q: set(map(add_block_to_db, q)),
            BLACKHOLE_EVADE_TIMER_SECS, list(block_q.queue))

    peer_sockets: List['socket.socket'] = []

    # Pick edges randomly
    # Using orderedset for the tried edges to ensure random pairing with queue
    tried_edges: OrderedSet['Peer'] = OrderedSet()

    while len(peer_sockets) < MAX_OUTBOUND_DANDELION_EDGE:
        try:
            peer_sockets.append(_setup_edge(peer_set, tried_edges))
        except NotEnoughEdges:
            logger.debug("Not able to build enough peers for stemout")
            break
        finally:
            if not d_phase.is_stem_phase() or d_phase.remaining_time() < 5:
                logger.error(
                    "Did not stem out any blocks in time, " +
                    "if this happens regularly you may be under attack",
                    terminal=True)


