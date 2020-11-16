"""Onionr - Private P2P Communication.

Use the communicator to insert fake mail messages
"""
import secrets

from etc import onionrvalues
import onionrblocks
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


def insert_deniable_block():
    """Insert a fake block to make it more difficult to track real blocks."""
    fakePeer = ''
    chance = 10
    if secrets.randbelow(chance) == (chance - 1):
        # This assumes on the libsodium primitives to have key-privacy
        fakePeer = onionrvalues.DENIABLE_PEER_ADDRESS
        data = secrets.token_hex(secrets.randbelow(5120) + 1)
        onionrblocks.insert(data, header='pm', encryptType='asym',
                            asymPeer=fakePeer, disableForward=True,
                            meta={'subject': 'foo'})
