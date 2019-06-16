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
def clean_old_blocks(comm_inst):
    '''Delete old blocks if our disk allocation is full/near full, and also expired blocks'''

    # Delete expired blocks
    for bHash in comm_inst._core.getExpiredBlocks():
        comm_inst._core._blacklist.addToDB(bHash)
        comm_inst._core.removeBlock(bHash)
        logger.info('Deleted block: %s' % (bHash,))

    while comm_inst._core._utils.storageCounter.isFull():
        oldest = comm_inst._core.getBlockList()[0]
        comm_inst._core._blacklist.addToDB(oldest)
        comm_inst._core.removeBlock(oldest)
        logger.info('Deleted block: %s' % (oldest,))

    comm_inst.decrementThreadCount('clean_old_blocks')

def clean_keys(comm_inst):
    '''Delete expired forward secrecy keys'''
    conn = sqlite3.connect(comm_inst._core.peerDB, timeout=10)
    c = conn.cursor()
    time = comm_inst._core._utils.getEpoch()
    deleteKeys = []

    for entry in c.execute("SELECT * FROM forwardKeys WHERE expire <= ?", (time,)):
        logger.debug('Forward key: %s' % entry[1])
        deleteKeys.append(entry[1])

    for key in deleteKeys:
        logger.debug('Deleting forward key %s' % key)
        c.execute("DELETE from forwardKeys where forwardKey = ?", (key,))
    conn.commit()
    conn.close()

    onionrusers.deleteExpiredKeys(comm_inst._core)

    comm_inst.decrementThreadCount('clean_keys')