import asyncio
from typing import TYPE_CHECKING
from typing import Set

from queue import Queue
from .connectpeer import connect_peer

from onionrplugins import onionrevents

if TYPE_CHECKING:
    from onionrblocks import Block
    from peer import Peer

from filepaths import gossip_server_socket_file
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


def gossip_server(
        peer_set: Set['Peer'],
        block_queue: Queue['Block'],
        dandelion_seed: bytes):

    async def peer_connected(reader, writer):
        while True:
            try:
                cmd = await asyncio.wait_for(reader.read(1), 60)
            except asyncio.exceptions.CancelledError:
                writer.close()

            cmd = int.from_bytes(cmd, 'big')
            if cmd == b'' or cmd == 0:
                continue
            match GossipCommands(cmd):
                case GossipCommands.PING:
                    writer.write(b'PONG')
                case GossipCommands.CLOSE:
                    writer.close()
                case GossipCommands.ANNOUNCE:
                    async def _read_announce():
                        address = await reader.read(56)
                        onionrevents.event(
                            'announce_rec',
                            data={'peer_set': peer_set,
                                  'address': address,
                                  'callback': connect_peer},
                            threaded=True)
                        writer.write(int(1).to_bytes(1, 'big'))
                    await asyncio.wait_for(_read_announce(), 10)

            await writer.drain()

    async def main():

        server = await asyncio.start_unix_server(
            peer_connected, gossip_server_socket_file
        )

        async with server:
            await server.serve_forever()

    asyncio.run(main())
