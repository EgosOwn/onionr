from queue import Queue
"""Onionr - Private P2P Communication.

block_queues where all received or created blocks are placed

Blocks are placed here before being sent to the network, the reason they are in
2 queues is for dandelion++ implementation.

The queues are drained randomly to incoming or outgoing edges depending on
dandelion++ phase
"""
from typing import Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from onionrblocks import Block
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

gossip_block_queues: Tuple["Queue[Block]", "Queue[Block]"] = (Queue(), Queue())
