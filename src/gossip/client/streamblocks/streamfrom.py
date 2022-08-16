"""Onionr - Private P2P Communication.

Download blocks that are being diffused

doesn't apply for blocks in the gossip queue that are awaiting
descision to fluff or stem
"""
from ast import Index
from threading import Thread, Semaphore
from random import SystemRandom
from time import sleep
import traceback
from typing import TYPE_CHECKING, List

import blockdb

from ...constants import BLOCK_ID_SIZE, BLOCK_MAX_SIZE, BLOCK_SIZE_LEN, BLOCK_STREAM_OFFSET_DIGITS

if TYPE_CHECKING:
    from socket import socket
    from gossip.peer import Peer

from ordered_set import OrderedSet

import logger

import onionrblocks
from ...peerset import gossip_peer_set
from ...commands import GossipCommands, command_to_byte

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


MAX_STREAMS = 6
CONNECT_TIMEOUT = 45
MAX_TRIED_PEERS = 10_000


def stream_from_peers():
    # Pick N peers to stream from
    # Create sockets for them
    # Spawn thread to stream from the socket

    tried_peers: OrderedSet['Peer'] = OrderedSet()

    sys_rand = SystemRandom()

    need_socket_lock = Semaphore(MAX_STREAMS)
    offset = 0


    def _stream_from_peer(peer: 'Peer'):
        stream_counter = 0
        stream_times = 100
        try:
            sock = peer.get_socket(CONNECT_TIMEOUT)
        except ConnectionRefusedError:
            need_socket_lock.release()
            return
        except Exception:
            logger.warn(traceback.format_exc(), terminal=True)
            need_socket_lock.release()
            return
        try:
            sock.sendall(
                command_to_byte(GossipCommands.STREAM_BLOCKS)
            )
            sock.sendall(
                str(offset).zfill(BLOCK_STREAM_OFFSET_DIGITS).encode('utf-8'))

            while stream_times >= stream_counter:
                stream_counter += 1
                #logger.debug("Reading block of id in stream with " + peer.transport_address, terminal=True)
                sock.settimeout(5)
                block_id = sock.recv(BLOCK_ID_SIZE)
                if blockdb.has_block(block_id):
                    sock.sendall(int(0).to_bytes(1, 'big'))
                    continue
                sock.sendall(int(1).to_bytes(1, 'big'))

                #logger.debug("Reading block size in stream", terminal=True)

                sock.settimeout(5)
                block_size = int(sock.recv(BLOCK_SIZE_LEN))
                if block_size > BLOCK_MAX_SIZE or block_size <= 0:
                    logger.warn(
                        f"Peer {peer.transport_address} " +
                        "reported block size out of range")
                    break

                sock.settimeout(5)
                block_data = sock.recv(block_size)

                #logger.debug(
                #    "We got a block from stream, assuming it is valid",
                #    terminal=True)
                try:
                    blockdb.add_block_to_db(
                        onionrblocks.Block(
                            block_id, block_data, auto_verify=True))
                except Exception:
                    # They gave us a bad block, kill the stream
                    # Could be corruption or malice
                    sock.sendall(int(0).to_bytes(1, 'big'))
                    raise
                # Tell them to keep streaming
                sock.sendall(int(1).to_bytes(1, 'big'))
        except (BrokenPipeError, TimeoutError) as e:
            pass
            #logger.debug(f"{e} when streaming from peers", terminal=True)
            #logger.debug(traceback.format_exc())
        except Exception:
            logger.warn(traceback.format_exc(), terminal=True)
        finally:
            sock.close()
            need_socket_lock.release()

    # spawn stream threads infinitely
    while True:
        if not gossip_peer_set:
            sleep(2)
        available_set = gossip_peer_set - tried_peers
        if not len(available_set) and len(tried_peers):
            try:
                tried_peers.clear()
            except IndexError:
                pass
            available_set = gossip_peer_set.copy()
        peers = sys_rand.sample(
            available_set,
            min(MAX_STREAMS, len(available_set)))

        tried_peers.update(peers)
        if len(tried_peers) >= MAX_TRIED_PEERS:
            tried_peers.pop()

        while len(peers):
            try:
                need_socket_lock.acquire()
                Thread(
                    target=_stream_from_peer,
                    args=[peers.pop()],
                    daemon=True,
                    name="_stream_from_peer").start()
            except IndexError:
                need_socket_lock.release()
                break

