"""Onionr - Private P2P Communication.

Dandelion ++ Gossip client logic
"""
import traceback
from typing import TYPE_CHECKING
from typing import Set
from time import sleep

from queue import Queue

if TYPE_CHECKING:
    from onionrblocks import Block
    from ..peer import Peer

import logger
import onionrplugins
from ..commands import GossipCommands
from gossip.phase import DandelionPhase
from onionrthreads import add_onionr_thread

from .announce import do_announce
from .peerexchange import get_new_peers
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


def gossip_client(
        peer_set: Set['Peer'],
        block_queue: Queue['Block'],
        dandelion_seed: bytes):
    """
    Gossip client does the following:

    Stem new blocks we created or downloaded *during stem phase*
    Stream new blocks
    """

    def _trigger_new_peers_event(new_peer_set: Set['Peer']):
        onionrplugins.events.event(
            'new_peer',
            data={'peers': peer_set, 'new_peers': new_peer_set})

    add_onionr_thread(do_announce, 3600, peer_set, initial_sleep=10)
    add_onionr_thread(
        get_new_peers,
        1200, peer_set,  _trigger_new_peers_event, initial_sleep=5)


    dandelion_phase = DandelionPhase(dandelion_seed, 30)
    while True:
        while not len(peer_set):
            sleep(0.2)
        if dandelion_phase.is_stem_phase():
            pass
        else:
            pass

