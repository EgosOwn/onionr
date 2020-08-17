"""Onionr - Private P2P Communication.

Work with information relating to blocks stored on the node
"""
import sqlite3

from etc import onionrvalues
from . import expiredblocks, updateblockinfo, add
from .. import dbfiles
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

update_block_info = updateblockinfo.update_block_info
add_to_block_DB = add.add_to_block_DB


def get_block_list(date_rec=None, unsaved=False):
    """Get list of our blocks."""
    if date_rec is None:
        date_rec = 0

    conn = sqlite3.connect(
        dbfiles.block_meta_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    execute = 'SELECT hash FROM hashes WHERE dateReceived' + \
        ' >= ? ORDER BY dateReceived ASC;'
    args = (date_rec,)
    rows = list()
    for row in c.execute(execute, args):
        for i in row:
            rows.append(i)
    conn.close()
    return rows


def get_block_date(blockHash):
    """Return the date a block was received."""
    conn = sqlite3.connect(
        dbfiles.block_meta_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    execute = 'SELECT dateReceived FROM hashes WHERE hash=?;'
    args = (blockHash,)
    for row in c.execute(execute, args):
        for i in row:
            return int(i)
    conn.close()
    return None


def get_blocks_by_type(blockType, orderDate=True):
    """Return a list of blocks by the type."""

    conn = sqlite3.connect(
        dbfiles.block_meta_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    if orderDate:
        execute = 'SELECT hash FROM hashes WHERE dataType=? ORDER BY dateReceived;'
    else:
        execute = 'SELECT hash FROM hashes WHERE dataType=?;'

    args = (blockType,)
    rows = list()

    for row in c.execute(execute, args):
        for i in row:
            rows.append(i)
    conn.close()
    return rows

