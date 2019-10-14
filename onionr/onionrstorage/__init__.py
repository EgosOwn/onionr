'''
    Onionr - Private P2P Communication

    This file handles block storage, providing an abstraction for storing blocks between file system and database
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
import sys, sqlite3, os
from onionrutils import bytesconverter, stringvalidators
from coredb import dbfiles
import filepaths, onionrcrypto, onionrexceptions
from onionrsetup import dbcreator
from onionrcrypto import hashers
from . import setdata
DB_ENTRY_SIZE_LIMIT = 10000 # Will be a config option

set_data = setdata.set_data

def _dbInsert(blockHash, data):
    conn = sqlite3.connect(dbfiles.block_data_db, timeout=10)
    c = conn.cursor()
    data = (blockHash, data)
    c.execute('INSERT INTO blockData (hash, data) VALUES(?, ?);', data)
    conn.commit()
    conn.close()

def _dbFetch(blockHash):
    conn = sqlite3.connect(dbfiles.block_data_db, timeout=10)
    c = conn.cursor()
    for i in c.execute('SELECT data from blockData where hash = ?', (blockHash,)):
        return i[0]
    conn.commit()
    conn.close()
    return None

def deleteBlock(blockHash):
    # You should call removeblock.remove_block if you automatically want to remove storage byte count
    if os.path.exists('%s/%s.dat' % (filepaths.block_data_location, blockHash)):
        os.remove('%s/%s.dat' % (filepaths.block_data_location, blockHash))
        return True
    conn = sqlite3.connect(dbfiles.block_data_db, timeout=10)
    c = conn.cursor()
    data = (blockHash,)
    c.execute('DELETE FROM blockData where hash = ?', data)
    conn.commit()
    conn.close()
    return True

def store(data, blockHash=''):
    if not stringvalidators.validate_hash(blockHash): raise ValueError
    ourHash = hashers.sha3_hash(data)
    if blockHash != '':
        if not ourHash == blockHash: raise ValueError('Hash specified does not meet internal hash check')
    else:
        blockHash = ourHash
    
    if DB_ENTRY_SIZE_LIMIT >= sys.getsizeof(data):
        _dbInsert(blockHash, data)
    else:
        with open('%s/%s.dat' % (filepaths.block_data_location, blockHash), 'wb') as blockFile:
            blockFile.write(data)

def getData(bHash):
    if not stringvalidators.validate_hash(bHash): raise ValueError

    bHash = bytesconverter.bytes_to_str(bHash)

    # First check DB for data entry by hash
    # if no entry, check disk
    # If no entry in either, raise an exception
    retData = None
    fileLocation = '%s/%s.dat' % (filepaths.block_data_location, bHash)
    if os.path.exists(fileLocation):
        with open(fileLocation, 'rb') as block:
            retData = block.read()
    else:
        retData = _dbFetch(bHash)
        if retData is None:
            raise onionrexceptions.NoDataAvailable("Block data for %s is not available" % [bHash])
    return retData