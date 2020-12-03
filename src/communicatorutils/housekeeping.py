"""Onionr - Private P2P Communication.

Cleanup old Onionr blocks and forward secrecy keys using the communicator.
Ran from a communicator timer usually
"""
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deadsimplekv import DeadSimpleKV

import logger
from onionrusers import onionrusers
from onionrutils import epoch
from coredb import blockmetadb, dbfiles
import onionrstorage
from onionrstorage import removeblock
from onionrblocks import onionrblacklist
from onionrblocks.storagecounter import StorageCounter
from etc.onionrvalues import DATABASE_LOCK_TIMEOUT
from onionrproofs import hashMeetsDifficulty
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

storage_counter = StorageCounter()


def __remove_from_upload(shared_state, block_hash: str):
    kv: "DeadSimpleKV" = shared_state.get_by_string("DeadSimpleKV")
    try:
        kv.get('blocksToUpload').remove(block_hash)
    except ValueError:
        pass


def __purge_block(shared_state, block_hash, add_to_blacklist = True):
    blacklist = None

    removeblock.remove_block(block_hash)
    onionrstorage.deleteBlock(block_hash)
    __remove_from_upload(shared_state, block_hash)

    if add_to_blacklist:
        blacklist = onionrblacklist.OnionrBlackList()
        blacklist.addToDB(block_hash)


def clean_old_blocks(shared_state):
    """Delete expired blocks + old blocks if disk allocation is near full"""
    blacklist = onionrblacklist.OnionrBlackList()
    # Delete expired blocks
    for bHash in blockmetadb.expiredblocks.get_expired_blocks():
        __purge_block(shared_state, bHash, add_to_blacklist=True)
        logger.info('Deleted expired block: %s' % (bHash,))

    while storage_counter.is_full():
        try:
            oldest = blockmetadb.get_block_list()[0]
        except IndexError:
            break
        else:
            __purge_block(shared_state, bHash, add_to_blacklist=True)
            logger.info('Deleted block because of full storage: %s' % (oldest,))


def clean_keys():
    """Delete expired forward secrecy keys"""
    conn = sqlite3.connect(dbfiles.user_id_info_db,
                           timeout=DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()
    time = epoch.get_epoch()
    deleteKeys = []

    for entry in c.execute(
            "SELECT * FROM forwardKeys WHERE expire <= ?", (time,)):
        logger.debug('Forward key: %s' % entry[1])
        deleteKeys.append(entry[1])

    for key in deleteKeys:
        logger.debug('Deleting forward key %s' % key)
        c.execute("DELETE from forwardKeys where forwardKey = ?", (key,))
    conn.commit()
    conn.close()

    onionrusers.deleteExpiredKeys()


def clean_blocks_not_meeting_pow(shared_state):
    """Clean blocks not meeting min send/rec pow. Used if config.json POW changes"""
    block_list = blockmetadb.get_block_list()
    for block in block_list:
        if not hashMeetsDifficulty(block):
            logger.warn(
                f"Deleting block {block} because it was stored" + 
                "with a POW level smaller than current.", terminal=True)
            __purge_block(shared_state, block)
