"""
Onionr - Private P2P Communication.

pick online peers in a communicator instance
"""
import secrets
from typing import TYPE_CHECKING

import onionrexceptions

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


def pick_online_peer(kv: 'DeadSimpleKV'):
    """Randomly picks peer from pool without bias (using secrets module)."""
    ret_data = ''
    peer_length = len(kv.get('onlinePeers'))
    if peer_length <= 0:
        raise onionrexceptions.OnlinePeerNeeded

    while True:
        peer_length = len(kv.get('onlinePeers'))

        try:
            # Get a random online peer, securely.
            # May get stuck in loop if network is lost
            ret_data = kv.get('onlinePeers')[secrets.randbelow(peer_length)]
        except IndexError:
            pass
        else:
            break
    return ret_data
