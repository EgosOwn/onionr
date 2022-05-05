"""Onionr - Private P2P Communication.

Dandelion ++ Gossip client logic
"""
import traceback
from typing import TYPE_CHECKING
from typing import Set, Tuple
from time import sleep
import asyncio

from queue import Queue


from onionrblocks import Block

from gossip.client.storeblocks import store_blocks

from ..constants import DANDELION_EPOCH_LENGTH
from ..connectpeer import connect_peer

if TYPE_CHECKING:
    from ..peer import Peer
    from ordered_set import OrderedSet

import logger
import onionrplugins
from ..commands import GossipCommands
from gossip.dandelion.phase import DandelionPhase
from onionrthreads import add_onionr_thread
from blockdb import add_block_to_db


from .announce import do_announce
from .dandelionstem import stem_out
from .peerexchange import get_new_peers
from ..peerset import gossip_peer_set
from .streamblocks import stream_from_peers

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


def gossip_client():
    """
    Gossip client does the following:

    Stem new blocks we created or downloaded *during stem phase*
    Stream new blocks
    """
    bl: Block
    do_announce()

    # Start a thread that runs every 1200 secs to
    # Ask peers for a subset for their peer set
    # The transport addresses for said peers will
    # be passed to a plugin event where the respective
    # transport plugin handles the new peer
    add_onionr_thread(
        get_new_peers,
        120, initial_sleep=5)

    # Start a new thread to stream blocks from peers


    dandelion_phase = DandelionPhase(DANDELION_EPOCH_LENGTH)

    while True:
        while not len(gossip_peer_set):
            sleep(0.2)
        if dandelion_phase.remaining_time() <= 10:
            sleep(dandelion_phase.remaining_time())
        if dandelion_phase.is_stem_phase():
            logger.debug("Entering stem phase", terminal=True)
            try:
                # Stem out blocks for (roughly) remaining epoch time
                asyncio.run(stem_out(dandelion_phase))
            except TimeoutError:
                continue
            except Exception:
                logger.error(traceback.format_exc(), terminal=True)
            continue
        else:
            logger.debug("Entering fluff phase", terminal=True)
            # Add block to primary block db, where the diffuser can read it
            store_blocks(dandelion_phase)
