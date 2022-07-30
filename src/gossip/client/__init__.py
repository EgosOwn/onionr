"""Onionr - Private P2P Communication.

Dandelion ++ Gossip client logic
"""
import traceback
from threading import Thread
from typing import TYPE_CHECKING
from typing import Set, Tuple
from time import sleep
import asyncio

from queue import Queue


from onionrblocks import Block

from ..constants import DANDELION_EPOCH_LENGTH
from ..connectpeer import connect_peer

if TYPE_CHECKING:
    from ..peer import Peer
    from ordered_set import OrderedSet

import logger
import config
import onionrplugins
from ..commands import GossipCommands
from gossip.dandelion.phase import DandelionPhase
from onionrthreads import add_onionr_thread
from blockdb import add_block_to_db


from .storeblocks import store_blocks
from .announce import do_announce
from .dandelionstem import stem_out
from .peerexchange import get_new_peers
from ..peerset import gossip_peer_set
from .streamblocks import stream_from_peers, stream_to_peer

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

dandelion_phase = DandelionPhase(DANDELION_EPOCH_LENGTH)


def block_queue_processing():


    while not len(gossip_peer_set):
        sleep(0.2)
    if dandelion_phase.remaining_time() <= 15:
        #logger.debug("Sleeping", terminal=True)
        sleep(dandelion_phase.remaining_time())
    if dandelion_phase.is_stem_phase() and config.get('security.dandelion.enabled', True):
        logger.debug("Entering stem phase", terminal=True)
        try:
            # Stem out blocks for (roughly) remaining epoch time
            asyncio.run(stem_out(dandelion_phase))
        except TimeoutError:
            pass
        except Exception:
            logger.error(traceback.format_exc(), terminal=True)
        pass
    else:
        #logger.debug("Entering fluff phase", terminal=True)
        # Add block to primary block db, where the diffuser can read it
        sleep(0.1)
        store_blocks(dandelion_phase)


def start_gossip_client():
    """
    Gossip client does the following:

    Stem new blocks we created or downloaded *during stem phase*
    Stream new blocks
    """
    bl: Block


    Thread(target=do_announce, daemon=True, name='do_announce').start()

    # Start a thread that runs every 1200 secs to
    # Ask peers for a subset for their peer set
    # The transport addresses for said peers will
    # be passed to a plugin event where the respective
    # transport plugin handles the new peer
    add_onionr_thread(
        get_new_peers,
        60, 'get_new_peers', initial_sleep=120)

    # Start a new thread to stream blocks from peers
    # These blocks are being diffused and are stored in
    # the peer's block database
    add_onionr_thread(
        stream_from_peers,
        3, 'stream_from_peers', initial_sleep=10
    )

    # Start a thread to upload blocks, useful for when
    # connectivity is poor or we are not allowing incoming
    # connections on any transports

    add_onionr_thread(
        stream_to_peer,
        10, 'stream_to_peer', initial_sleep=1)

    # Blocks we receive or create through all means except
    # Diffusal are put into block queues, we decide to either
    # stem or diffuse a block from the queue based on the current
    # dandelion++ phase
    while True:
        block_queue_processing()
