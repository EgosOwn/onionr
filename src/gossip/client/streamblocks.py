"""Onionr - Private P2P Communication.

Download blocks that are being diffused

doesn't apply for blocks in the gossip queue that are awaiting
descision to fluff or stem

"""
from random import SystemRandom

if TYPE_CHECKING:
    from socket import socket
    from typing import TYPE_CHECKING, List

from ..peerset import gossip_peer_set

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


def stream_from_peers():
    peer_stream_sockets: List[socket] = []

    sys_rand = SystemRandom()

    while True:
        peers = sys_rand.sample(gossip_peer_set, min(3, len(gossip_peer_set)))
