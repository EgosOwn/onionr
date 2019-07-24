'''
    Onionr - Private P2P Communication

    This module works with information relating to blocks stored on the node
'''
'''
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
'''
import sqlite3
from . import expiredblocks, updateblockinfo, add
from .. import dbfiles
update_block_info = updateblockinfo.update_block_info
add_to_block_DB = add.add_to_block_DB
def get_block_list(dateRec = None, unsaved = False):
    '''
        Get list of our blocks
    '''
    if dateRec == None:
        dateRec = 0

    conn = sqlite3.connect(dbfiles.block_meta_db, timeout=30)
    c = conn.cursor()

    execute = 'SELECT hash FROM hashes WHERE dateReceived >= ? ORDER BY dateReceived ASC;'
    args = (dateRec,)
    rows = list()
    for row in c.execute(execute, args):
        for i in row:
            rows.append(i)
    conn.close()
    return rows

def get_block_date(blockHash):
    '''
        Returns the date a block was received
    '''

    conn = sqlite3.connect(dbfiles.block_meta_db, timeout=30)
    c = conn.cursor()

    execute = 'SELECT dateReceived FROM hashes WHERE hash=?;'
    args = (blockHash,)
    for row in c.execute(execute, args):
        for i in row:
            return int(i)
    conn.close()
    return None

def get_blocks_by_type(blockType, orderDate=True):
    '''
        Returns a list of blocks by the type
    '''

    conn = sqlite3.connect(dbfiles.block_meta_db, timeout=30)
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