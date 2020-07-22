"""
Onionr - Private P2P Communication.

Pick a proxy to use based on a peer's address
"""
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


def pick_proxy(peer_address):
    if peer_address.endswith('.onion'):
        return 'tor'
    elif peer_address.endswith('.i2p'):
        return 'i2p'
    raise ValueError(
        f"Peer address not ending with acceptable domain: {peer_address}")
