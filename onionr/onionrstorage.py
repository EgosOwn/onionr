'''
    Onionr - P2P Anonymous Storage Network

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
import core, sys, sqlite3, os, dbcreator

DB_ENTRY_SIZE_LIMIT = 10000 # Will be a config option

def dbCreate(coreInst):
    try:
        dbcreator.DBCreator(coreInst).createBlockDataDB()
    except FileExistsError:
        pass

def _dbInsert(coreInst, blockHash, data):
    assert isinstance(coreInst, core.Core)
    dbCreate(coreInst)
    conn = sqlite3.connect(coreInst.blockDataDB, timeout=10)
    c = conn.cursor()
    data = (blockHash, data)
    c.execute('INSERT INTO blockData (hash, data) VALUES(?, ?);', data)
    conn.commit()
    conn.close()

def _dbFetch(coreInst, blockHash):
    assert isinstance(coreInst, core.Core)
    dbCreate(coreInst)
    conn = sqlite3.connect(coreInst.blockDataDB, timeout=10)
    c = conn.cursor()
    for i in c.execute('SELECT data from blockData where hash = ?', (blockHash,)):
        return i[0]
    conn.commit()
    conn.close()
    return None

def store(coreInst, data, blockHash=''):
    assert isinstance(coreInst, core.Core)
    assert coreInst._utils.validateHash(blockHash)
    ourHash = coreInst._crypto.sha3Hash(data)
    if blockHash != '':
        assert ourHash == blockHash
    else:
        blockHash = ourHash
    
    if DB_ENTRY_SIZE_LIMIT >= sys.getsizeof(data):
        _dbInsert(coreInst, blockHash, data)
    else:
        with open('%s/%s.dat' % (coreInst.blockDataLocation, blockHash), 'wb') as blockFile:
            blockFile.write(data)

def getData(coreInst, bHash):
    assert isinstance(coreInst, core.Core)
    assert coreInst._utils.validateHash(bHash)

    # First check DB for data entry by hash
    # if no entry, check disk
    # If no entry in either, raise an exception
    retData = ''
    fileLocation = '%s/%s.dat' % (coreInst.blockDataLocation, bHash)
    if os.path.exists(fileLocation):
        with open(fileLocation, 'rb') as block:
            retData = block.read()
    else:
        retData = _dbFetch(coreInst, bHash)
    return retData