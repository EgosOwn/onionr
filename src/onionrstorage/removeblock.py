"""Onionr - Private P2P Communication.

remove onionr block from meta db
"""
import sys
import sqlite3

import onionrexceptions
import onionrstorage
from onionrutils import stringvalidators
from coredb import dbfiles
from onionrblocks import storagecounter
from etc.onionrvalues import DATABASE_LOCK_TIMEOUT
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


def remove_block(block):
    """Remove a block from this node.

    (does not automatically blacklist).
    **You may want blacklist.addToDB(blockHash)
    """
    if stringvalidators.validate_hash(block):
        conn = sqlite3.connect(
            dbfiles.block_meta_db, timeout=DATABASE_LOCK_TIMEOUT)
        c = conn.cursor()
        t = (block,)
        c.execute('Delete from hashes where hash=?;', t)
        conn.commit()
        conn.close()
        dataSize = sys.getsizeof(onionrstorage.getData(block))
        storagecounter.StorageCounter().remove_bytes(dataSize)
    else:
        raise onionrexceptions.InvalidHexHash
