"""Onionr - Private P2P Communication.

Add an entry to the block metadata database
"""
import sqlite3
import secrets
from onionrutils import epoch
from onionrblocks import blockmetadata
from etc import onionrvalues
from .. import dbfiles
from onionrexceptions import BlockMetaEntryExists
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


def add_to_block_DB(newHash, selfInsert=False, dataSaved=False):
    """
        Add a hash value to the block db

        Should be in hex format!
    """

    if blockmetadata.has_block(newHash):
        raise BlockMetaEntryExists
    conn = sqlite3.connect(
        dbfiles.block_meta_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()
    currentTime = epoch.get_epoch() + secrets.randbelow(61)
    if selfInsert or dataSaved:
        selfInsert = 1
    else:
        selfInsert = 0
    data = (newHash, currentTime, '', selfInsert)
    c.execute(
        'INSERT INTO hashes (hash, dateReceived, dataType, dataSaved) VALUES(?, ?, ?, ?);', data)
    conn.commit()
    conn.close()
