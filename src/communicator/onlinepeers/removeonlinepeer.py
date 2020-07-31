"""Onionr - Private P2P Communication.

remove an online peer from the pool in a communicator instance
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deadsimplekv import DeadSimpleKV
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


def remove_online_peer(kv, peer):
    """Remove an online peer."""
    try:
        del kv.get('connectTimes')[peer]
    except KeyError:
        pass
    try:
        del kv.get('dbTimestamps')[peer]
    except KeyError:
        pass
    try:
        kv.get('onlinePeers').remove(peer)
    except ValueError:
        pass
