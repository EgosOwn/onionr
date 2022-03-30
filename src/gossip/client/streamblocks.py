"""Onionr - Private P2P Communication.

Download blocks that are being diffused

doesn't apply for blocks in the gossip queue that are awaiting
descision to fluff or stem

"""
from threading import Thread, Semaphore
from random import SystemRandom
from time import sleep
import traceback

if TYPE_CHECKING:
    from socket import socket
    from typing import TYPE_CHECKING, List
    from gossip.peer import Peer

from ordered_set import OrderedSet

import logger

from ..peerset import gossip_peer_set
from ..commands import GossipCommands, command_to_byte

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


MAX_STREAMS = 3
CONNECT_TIMEOUT = 12
MAX_TRIED_PEERS = 10_000

def stream_from_peers():
    # Pick N peers to stream from
    # Create sockets for them
    # Spawn thread to stream from the socket

    tried_peers: OrderedSet[Peer] = OrderedSet()

    sys_rand = SystemRandom()

    need_socket_lock = Semaphore(MAX_STREAMS)

    def _stream_from_peer(peer: Peer):

        try:
            sock = peer.get_socket(CONNECT_TIMEOUT)
            sock.sendall(
                command_to_byte(GossipCommands.STREAM_BLOCKS)
            )
        except Exception:
            logger.warn(traceback.format_exc())
            sock.close()
            need_socket_lock.release()

    while True:
        need_socket_lock.acquire()
        available_set = gossip_peer_set - tried_peers
        peers = sys_rand.sample(
            available_set,
            min(MAX_STREAMS, len(available_set)))

        tried_peers.update(peers)
        if len(tried_peers) >= MAX_TRIED_PEERS:
            tried_peers.pop()

        while len(peers):
            try:
                Thread(
                    target=_stream_from_peer,
                    args=[peers.pop()],
                    daemon=True).start()
            except IndexError:
                need_socket_lock.release()
                break
