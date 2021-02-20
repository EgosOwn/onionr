"""Onionr - Private P2P Communication.

Fanout blocks to Onionr TorGossip peer
"""
import os
import sys
from typing import TYPE_CHECKING
from random import SystemRandom

if TYPE_CHECKING:
    from socket import socket

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from commands import GossipCommands
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


def fanout_to_peers(
        socket_pool: dict,
        block_hash: bytes,
        block_data: 'KastenPacked',
        fanout_count: int = 4):
    peers_to_use = []
    peers = list(socket_pool)
    SystemRandom().shuffle(peers)

    for i in range(fanout_count):
        peer: 'socket' = peers.pop()
        peer.sendall(G)

