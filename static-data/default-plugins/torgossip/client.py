"""Onionr - Private P2P Communication.

Torgossip client

Create streams to random peers
"""
from os import path
from typing import TYPE_CHECKING
from random import SystemRandom

from netcontroller.torcontrol.onionserviceonline import service_online_recently
from netcontroller.torcontrol import torcontroller

if TYPE_CHECKING:
    from .peerdb import TorGossipPeers
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


def _add_bootstrap_peers(peer_db: 'TorGossipPeers'):
    bootstap_peers = path.dirname(path.realpath(__file__)) + "/bootstrap.txt"
    with open(bootstap_peers, 'r') as bs_peers:
        peers = bs_peers.split(',')
        for peer in peers:
            if peer:
                peer_db.add_peer(peer)


def _client_pool(shared_state, controller):
    peer_db: 'TorGossipPeers' = shared_state.get_by_string('TorGossipPeers')
    socket_pool = {}

    peers = peer_db.get_highest_score_peers(20)
    SystemRandom().shuffle(peers)

    for peer in peers:
        if not service_online_recently(controller, peer):
            continue

def client_pool(shared_state):
    controller = torcontroller.get_controller()
    # Pass the stem Controller and then close it even if an exception raises
    try:
        _client_pool(shared_state, controller)
    except Exception:
        raise
    finally:
        # Calls before the above raise no matter what
        controller.close()


