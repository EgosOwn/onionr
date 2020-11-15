"""Onionr - Private P2P Communication.

Check if a block should be downloaded
(if we already have it or its blacklisted or not)
"""
from coredb import blockmetadb
from onionrblocks import onionrblacklist
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


def should_download(shared_state, block_hash) -> bool:
    """Return bool for if a (assumed to exist) block should be downloaded."""
    blacklist = onionrblacklist.OnionrBlackList()
    should = True
    kv: "DeadSimpleKV" = shared_state.get_by_string("DeadSimpleKV")
    if block_hash in blockmetadb.get_block_list():
        # Don't download block we have
        should = False
    else:
        if blacklist.inBlacklist(block_hash):
            # Don't download blacklisted block
            should = False
    if should is False:
        # Remove block from communicator queue if it shouldn't be downloaded
        try:
            del kv.get('blockQueue')[block_hash]
        except KeyError:
            pass
    return should
