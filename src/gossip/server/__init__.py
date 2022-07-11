import asyncio
import traceback
from typing import TYPE_CHECKING
from typing import Set, Tuple

from queue import Queue

from gossip import constants
from ..connectpeer import connect_peer

from onionrplugins import onionrevents
import logger

if TYPE_CHECKING:
    from onionrblocks import Block
    from peer import Peer
    from ordered_set import OrderedSet
    from asyncio import StreamReader, StreamWriter

from filepaths import gossip_server_socket_file
from ..commands import GossipCommands
from ..peerset import gossip_peer_set
from .acceptstem import accept_stem_blocks
from .diffuseblocks import diffuse_blocks
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

inbound_dandelion_edge_count = [0]


def gossip_server():

    async def peer_connected(
            reader: 'StreamReader', writer: 'StreamWriter'):

        while True:
            try:
                cmd = await asyncio.wait_for(reader.readexactly(1), 60)
            except asyncio.exceptions.CancelledError:
                break
            except asyncio.IncompleteReadError:
                break

            cmd = int.from_bytes(cmd, 'big')
            if cmd == b'' or cmd == 0:
                continue
            match GossipCommands(cmd):
                case GossipCommands.PING:
                    writer.write(b'PONG')
                case GossipCommands.ANNOUNCE:
                    async def _read_announce():
                        address = await reader.readuntil(b'\n')

                        if address:
                            onionrevents.event(
                                'announce_rec',
                                data={'address': address,
                                      'callback': connect_peer},
                                threaded=True)
                            writer.write(int(1).to_bytes(1, 'big'))
                            await writer.drain()
                    await asyncio.wait_for(_read_announce(), 10)
                case GossipCommands.PEER_EXCHANGE:

                    for peer in gossip_peer_set:
                        writer.write(peer.transport_address.encode('utf-8') + b'\n')
                        await writer.drain()
                case GossipCommands.STREAM_BLOCKS:
                    try:
                        await diffuse_blocks(reader, writer)
                    except Exception:
                        logger.warn(
                            f"Err streaming blocks\n{traceback.format_exc()}",
                            terminal=True)
                case GossipCommands.PUT_BLOCKS:
                    # Pick block queue & append stemmed blocks to it
                    try:
                        await accept_stem_blocks(
                            reader, writer,
                            inbound_dandelion_edge_count)
                    except asyncio.exceptions.TimeoutError:
                        pass
                        logger.debug(
                            "Inbound edge timed out when steming blocks to us",
                            terminal=True)
                    except asyncio.exceptions.IncompleteReadError:
                        pass
                        logger.debug(
                            "Inbound edge timed out (Incomplete Read) when steming blocks to us",
                            terminal=True)
                    except Exception:
                        logger.warn(
                            f"Err accepting stem blocks\n{traceback.format_exc()}",
                            terminal=True)
                    # Subtract dandelion edge, make sure >=0
                    inbound_dandelion_edge_count[0] = \
                        max(inbound_dandelion_edge_count[0] - 1, 0)
            break

        await writer.drain()

    async def main():

        server = await asyncio.start_unix_server(
            peer_connected, gossip_server_socket_file
        )
        async with server:
            await server.serve_forever()

    asyncio.run(main())
