"""Onionr - Private P2P Communication.

import new blocks from disk, providing transport agnosticism
"""
import glob

import logger
from onionrblocks import blockmetadata
from coredb import blockmetadb
import filepaths
import onionrcrypto as crypto
from etc.onionrvalues import BLOCK_EXPORT_FILE_EXT
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


def import_new_blocks(scanDir=''):
    """Scan for new blocks ON THE DISK and import them"""
    blockList = blockmetadb.get_block_list()
    exist = False
    if scanDir == '':
        scanDir = filepaths.block_data_location
    if not scanDir.endswith('/'):
        scanDir += '/'
    for block in glob.glob(scanDir + "*%s" % (BLOCK_EXPORT_FILE_EXT,)):
        if block.replace(scanDir, '').replace(BLOCK_EXPORT_FILE_EXT, '') \
                not in blockList:
            exist = True
            logger.info('Found new block on dist %s' % block, terminal=True)
            with open(block, 'rb') as newBlock:
                block = block.replace(scanDir, '').replace(
                    BLOCK_EXPORT_FILE_EXT, '')
                if crypto.hashers.sha3_hash(newBlock.read()) == block.replace(
                        BLOCK_EXPORT_FILE_EXT, ''):
                    blockmetadb.add_to_block_DB(block.replace(
                        BLOCK_EXPORT_FILE_EXT, ''), dataSaved=True)
                    logger.info('Imported block %s' % block, terminal=True)
                    blockmetadata.process_block_metadata(block)
                else:
                    logger.warn('Failed to verify hash for %s' % block,
                                terminal=True)
    if not exist:
        logger.info('No blocks found to import', terminal=True)


import_new_blocks.onionr_help = \
    f"Scan the Onionr data directory under {filepaths.block_data_location}" + \
    "for new block files (.db not supported) to import"
