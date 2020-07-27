"""Onionr - P2P Anonymous Storage Network.

Remove block hash from daemon's upload list.
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deadsimplekv import DeadSimpleKV
    from communicator import OnionrCommunicatorDaemon
    from onionrtypes import BlockHash
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


def remove_from_insert_queue(comm_inst: "OnionrCommunicatorDaemon",
                             b_hash: "BlockHash"):
    """Remove block hash from daemon's upload list."""
    kv: "DeadSimpleKV" = comm_inst.shared_state.get_by_string("DeadSimpleKV")
    try:
        kv.get('generating_blocks').remove(b_hash)
    except ValueError:
        pass
