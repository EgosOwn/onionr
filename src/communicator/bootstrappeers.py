"""Onionr - Private P2P Communication.

add bootstrap peers to the communicator peer list
"""
from typing import TYPE_CHECKING

from utils import readstatic, gettransports
from coredb import keydb
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

bootstrap_peers = readstatic.read_static('bootstrap-nodes.txt').split(',')


def add_bootstrap_list_to_peer_list(kv, peerList, db_only=False):
    """Add the bootstrap list to the peer list (no duplicates)."""
    for i in bootstrap_peers:
        # Add bootstrap peers to peerList (does not save them)
        # Don't add them if they're already added or in the offline list
        if i not in peerList and i not in kv.get('offlinePeers') \
                and i not in gettransports.get() and len(str(i).strip()) > 0:
            if not db_only:
                peerList.append(i)
            keydb.addkeys.add_address(i)
