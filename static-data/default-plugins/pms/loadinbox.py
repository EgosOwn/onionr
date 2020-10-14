"""Onionr - Private P2P Communication.

Load the user's inbox and return it as a list
"""
from onionrblocks import onionrblockapi
from coredb import blockmetadb
from utils import reconstructhash, identifyhome
import deadsimplekv as simplekv
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

inbox_cache = {}
def load_inbox():
    inbox_list = []
    deleted = simplekv.DeadSimpleKV(identifyhome.identify_home() + '/mailcache.dat').get('deleted_mail')
    if deleted is None:
        deleted = []

    for blockHash in blockmetadb.get_blocks_by_type('pm'):
        if blockHash in deleted:
            continue
        if blockHash in inbox_cache:
            inbox_list.append(blockHash)
            continue
        block = onionrblockapi.Block(blockHash)
        block.decrypt()
        if block.decrypted and reconstructhash.deconstruct_hash(blockHash):
            inbox_cache[blockHash] = True
            inbox_list.append(blockHash)
    return inbox_list
