from collections import deque
from queue import Empty, Queue
from time import sleep
from secrets import choice
import traceback

from typing import TYPE_CHECKING, Coroutine, List

from ordered_set import OrderedSet

import config
from onionrthreads import add_delayed_thread
from blockdb import add_block_to_db
import logger

from ...constants import BLACKHOLE_EVADE_TIMER_SECS, OUTBOUND_DANDELION_EDGES
from ...commands import GossipCommands, command_to_byte
from ... import dandelion
from ...blockqueues import gossip_block_queues
from ...peerset import gossip_peer_set

from .stemstream import do_stem_stream

if TYPE_CHECKING:
    from ...peer import Peer
    from ...dandelion.phase import DandelionPhase
    import socket


class NotEnoughEdges(ValueError): pass  # noqa
class StemConnectionDenied(ConnectionRefusedError): pass  # noqa


async def _setup_edge(
        peer_set: "OrderedSet[Peer]", exclude_set: "OrderedSet[Peer]"):
    """Negotiate stem connection with random peer, add to exclu set if fail"""
    try:
        peer: 'Peer' = choice(peer_set - exclude_set)
    except IndexError:
        raise NotEnoughEdges

    # If peer is good or bad, exclude it no matter what
    exclude_set.add(peer)

    try:
        s = peer.get_socket(12)
    except TimeoutError:
        logger.debug(f"{peer.transport_address} timed out when trying stemout")
    except Exception:
        logger.debug(traceback.format_exc())
        return

    try:
        s.sendall(command_to_byte(GossipCommands.PUT_BLOCKS))
        s.settimeout(10)
        if s.recv(1) == dandelion.StemAcceptResult.DENY:
            raise StemConnectionDenied
    except TimeoutError:
        logger.debug(
            "Peer timed out when establishing stem connection", terminal=True)
        logger.debug(traceback.format_exc())
    except StemConnectionDenied:
        logger.debug(
            "Stem connection denied (peer has too many) " +
            f"{peer.transport_address}")
        logger.debug(traceback.format_exc())
    except Exception:
        logger.warn(
            "Error asking peer to establish stem connection" +
            traceback.format_exc(), terminal=True)
    else:
        # Return peer socket if it is in stem reception mode successfully
        return s

    # If they won't accept stem blocks, close the socket
    s.close()


async def stem_out(d_phase: 'DandelionPhase'):

    # don't bother if there are no possible outbound edges
    if not len(gossip_peer_set):
        sleep(1)
        return
    not_enough_edges = False
    strict_dandelion = config.get('security.dandelion.strict', True)

    def blackhole_protection(q):
        for bl in q:
            add_block_to_db(bl)


    # Spawn threads with deep copied block queue to add to db after time
    # for black hole attack
    for block_q in gossip_block_queues:
        add_delayed_thread(blackhole_protection, BLACKHOLE_EVADE_TIMER_SECS, block_q.queue)

    peer_sockets: List['socket.socket'] = []
    stream_routines: List[Coroutine] = []

    # Pick edges randomly
    # Using orderedset for the tried edges to ensure random pairing with queue
    tried_edges: "OrderedSet[Peer]" = OrderedSet()

    while len(peer_sockets) < OUTBOUND_DANDELION_EDGES or not_enough_edges:
        if gossip_block_queues[0].qsize() == 0 and \
                gossip_block_queues[1].qsize() == 0:
            sleep(1)
            continue
        try:
            # Get a socket for stem out (makes sure they accept)
            peer_sockets.append(
                await _setup_edge(gossip_peer_set, tried_edges))
        except NotEnoughEdges:
            # No possible edges at this point (edges < OUTBOUND_DANDELION_EDGE)
            #logger.debug(
            #    "Making too few edges for stemout " +
            #    "this is bad for anonymity if frequent.",
            #    terminal=True)
            if strict_dandelion:
                not_enough_edges = True
            else:
                if peer_sockets:
                    # if we have at least 1 peer,
                    # do dandelion anyway in non strict mode
                    # Allow poorly connected networks to communicate faster
                    for block in gossip_block_queues[1].queue:
                        gossip_block_queues[0].put_nowait(block)
                    else:
                        gossip_block_queues[1].queue = deque()
                    break
            sleep(1)
        else:
            # Ran out of time for stem phase
            if not d_phase.is_stem_phase() or d_phase.remaining_time() < 5:
                logger.error(
                    "Did not stem out any blocks in time, " +
                    "if this happens regularly you may be under attack",
                    terminal=False)
                for s in peer_sockets:
                    if s:
                        s.close()
                peer_sockets.clear()
                break
    # If above loop ran out of time or NotEnoughEdges,
    # loops below will not execute

    for count, peer_socket in enumerate(peer_sockets):
        stream_routines.append(
            do_stem_stream(peer_socket, gossip_block_queues[count], d_phase))

    for routine in stream_routines:
        try:
            await routine
        except Empty:
            pass
        except Exception:
            logger.warn(traceback.format_exc())
        else:
            # stream routine exited early
            pass
