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
from .acceptstem import accept_stem_blocks
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


def gossip_server(
        peer_set: "OrderedSet[Peer]",
        block_queues: Tuple["Queue[Block]", "Queue[Block]"],
        dandelion_seed: bytes):

    async def peer_connected(
            reader: 'StreamReader', writer: 'StreamWriter'):

        while True:
            try:
                cmd = await asyncio.wait_for(reader.read(1), 60)
            except asyncio.exceptions.CancelledError:
                break

            cmd = int.from_bytes(cmd, 'big')
            if cmd == b'' or cmd == 0:
                continue
            match GossipCommands(cmd):
                case GossipCommands.PING:
                    writer.write(b'PONG')
                case GossipCommands.CLOSE:
                    pass
                case GossipCommands.ANNOUNCE:
                    async def _read_announce():
                        address = await reader.read(
                            constants.TRANSPORT_SIZE_BYTES)
                        onionrevents.event(
                            'announce_rec',
                            data={'peer_set': peer_set,
                                  'address': address,
                                  'callback': connect_peer},
                            threaded=True)
                        writer.write(int(1).to_bytes(1, 'big'))
                    await asyncio.wait_for(_read_announce(), 10)
                case GossipCommands.PEER_EXCHANGE:
                    for peer in peer_set:
                        writer.write(
                            peer.transport_address.encode(
                                'utf-8').removesuffix(b'.onion'))
                case GossipCommands.PUT_BLOCKS:
                    # Create block queue & append stemmed blocks to it

                    try:
                        await accept_stem_blocks(
                            block_queues,
                            reader, writer,
                            inbound_dandelion_edge_count)
                    except Exception:
                        logger.warn(
                            f"Err getting\n{traceback.format_exc()}",
                            terminal=True)
                    # Subtract dandelion edge, make sure >=0
                    inbound_dandelion_edge_count[0] = \
                        max(inbound_dandelion_edge_count[0] - 1, 0)
            break

        await writer.drain()
        writer.close()

    async def main():

        server = await asyncio.start_unix_server(
            peer_connected, gossip_server_socket_file
        )

        async with server:
            await server.serve_forever()

    asyncio.run(main())
