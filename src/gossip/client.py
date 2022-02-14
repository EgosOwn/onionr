"""Onionr - Private P2P Communication.

Dandelion ++ Gossip client logic
"""
from typing import TYPE_CHECKING
from typing import Set

from queue import Queue

if TYPE_CHECKING:
    from onionrblocks import Block
    from .peer import Peer

import onionrplugins
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
    onionrplugins.events.event('')
