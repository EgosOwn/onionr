"""Onionr - Private P2P Communication.

Handle block storage, providing an abstraction for
storing blocks between file system and database
"""
import sys
import sqlite3
import os
from onionrutils import bytesconverter
from onionrutils import stringvalidators
from coredb import dbfiles
from filepaths import block_data_location
import onionrexceptions
from onionrcrypto import hashers
from . import setdata, removeblock
from etc.onionrvalues import DATABASE_LOCK_TIMEOUT, BLOCK_EXPORT_FILE_EXT
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


DB_ENTRY_SIZE_LIMIT = 10000  # Will be a config option

set_data = setdata.set_data


def _dbInsert(block_hash, data):
    conn = sqlite3.connect(dbfiles.block_data_db,
                           timeout=DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()
    data = (block_hash, data)
    c.execute('INSERT INTO blockData (hash, data) VALUES(?, ?);', data)
    conn.commit()
    conn.close()


def _dbFetch(block_hash):
    conn = sqlite3.connect(dbfiles.block_data_db,
                           timeout=DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()
    for i in c.execute(
            'SELECT data from blockData where hash = ?', (block_hash,)):
        return i[0]
    conn.commit()
    conn.close()
    return None


def deleteBlock(block_hash):
    # Call removeblock.remove_block to automatically want to remove storage byte count
    if os.path.exists(f'{block_data_location}/{block_hash}{BLOCK_EXPORT_FILE_EXT}'):
        os.remove(f'{block_data_location}/{block_hash}{BLOCK_EXPORT_FILE_EXT}')
        return True
    conn = sqlite3.connect(dbfiles.block_data_db,
                           timeout=DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()
    data = (block_hash,)
    c.execute('DELETE FROM blockData where hash = ?', data)
    conn.commit()
    conn.close()
    return True


def store(data, block_hash=''):
    if not stringvalidators.validate_hash(block_hash):
        raise ValueError
    ourHash = hashers.sha3_hash(data)
    if block_hash != '':
        if not ourHash == block_hash:
            raise ValueError('Hash specified does not meet internal hash check')
    else:
        block_hash = ourHash

    if DB_ENTRY_SIZE_LIMIT >= sys.getsizeof(data):
        _dbInsert(block_hash, data)
    else:
        with open(
                f'{block_data_location}/{block_hash}{BLOCK_EXPORT_FILE_EXT}', 'wb') as blck_file:
            blck_file.write(data)


def getData(bHash):

    if not stringvalidators.validate_hash(bHash):
        raise ValueError

    bHash = bytesconverter.bytes_to_str(bHash)
    bHash = bHash.strip()
    # First check DB for data entry by hash
    # if no entry, check disk
    # If no entry in either, raise an exception
    ret_data = None
    fileLocation = '%s/%s%s' % (
        block_data_location,
        bHash, BLOCK_EXPORT_FILE_EXT)
    not_found_msg = "Block data not found for: " + str(bHash)
    if os.path.exists(fileLocation):
        with open(fileLocation, 'rb') as block:
            ret_data = block.read()
    else:
        ret_data = _dbFetch(bHash)

        if ret_data is None:
            raise onionrexceptions.NoDataAvailable(not_found_msg)
    return ret_data
