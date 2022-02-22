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
    from .peer import Peer

import logger
import onionrplugins
from .commands import GossipCommands
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

    remove_peers = []

    while True:
        remove_peers.clear()
        for peer in peer_set:
            try:
                sock = peer.get_socket()
            except Exception:
                logger.warn("Lost connection to " + peer.transport_address)
                logger.warn(traceback.format_exc())
                remove_peers.append(peer)
                break
            sock.sendall(int(GossipCommands.PING).to_bytes(1, 'big'))
            if sock.recv(10) == b"PONG":
                print("Got ping at peer")
        while len(remove_peers):
            try:
                peer_set.remove(remove_peers.pop())
            except KeyError:
                pass

        sleep(30)
    return
