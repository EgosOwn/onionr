'''
    Onionr - Private P2P Communication

    Cleanup old Onionr blocks and forward secrecy keys using the communicator. Ran from a timer usually
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
import logger
from onionrusers import onionrusers
from onionrutils import epoch
from coredb import blockmetadb, dbfiles
import onionrstorage
from onionrstorage import removeblock
import onionrblacklist
def clean_old_blocks(comm_inst):
    '''Delete old blocks if our disk allocation is full/near full, and also expired blocks'''
    blacklist = onionrblacklist.OnionrBlackList()
    # Delete expired blocks
    for bHash in blockmetadb.expiredblocks.get_expired_blocks():
        blacklist.addToDB(bHash)
        removeblock.remove_block(bHash)
        onionrstorage.deleteBlock(bHash)
        logger.info('Deleted block: %s' % (bHash,))

    while comm_inst.storage_counter.isFull():
        oldest = blockmetadb.get_block_list()[0]
        blacklist.addToDB(oldest)
        removeblock.remove_block(oldest)
        onionrstorage.deleteBlock(bHash)
        logger.info('Deleted block: %s' % (oldest,))

    comm_inst.decrementThreadCount('clean_old_blocks')

def clean_keys(comm_inst):
    '''Delete expired forward secrecy keys'''
    conn = sqlite3.connect(dbfiles.user_id_info_db, timeout=10)
    c = conn.cursor()
    time = epoch.get_epoch()
    deleteKeys = []

    for entry in c.execute("SELECT * FROM forwardKeys WHERE expire <= ?", (time,)):
        logger.debug('Forward key: %s' % entry[1])
        deleteKeys.append(entry[1])

    for key in deleteKeys:
        logger.debug('Deleting forward key %s' % key)
        c.execute("DELETE from forwardKeys where forwardKey = ?", (key,))
    conn.commit()
    conn.close()

    onionrusers.deleteExpiredKeys()

    comm_inst.decrementThreadCount('clean_keys')