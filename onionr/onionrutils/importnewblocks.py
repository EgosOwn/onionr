'''
    Onionr - Private P2P Communication

    import new blocks from disk, providing transport agnosticism
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
import glob
import logger, core
from onionrutils import blockmetadata
from coredb import blockmetadb
def import_new_blocks(core_inst=None, scanDir=''):
    '''
        This function is intended to scan for new blocks ON THE DISK and import them
    '''
    if core_inst is None:
        core_inst = core.Core()
    blockList = blockmetadb.get_block_list()
    exist = False
    if scanDir == '':
        scanDir = core_inst.blockDataLocation
    if not scanDir.endswith('/'):
        scanDir += '/'
    for block in glob.glob(scanDir + "*.dat"):
        if block.replace(scanDir, '').replace('.dat', '') not in blockList:
            exist = True
            logger.info('Found new block on dist %s' % block, terminal=True)
            with open(block, 'rb') as newBlock:
                block = block.replace(scanDir, '').replace('.dat', '')
                if core_inst._crypto.sha3Hash(newBlock.read()) == block.replace('.dat', ''):
                    blockmetadb.add_to_block_DB(block.replace('.dat', ''), dataSaved=True)
                    logger.info('Imported block %s.' % block, terminal=True)
                    blockmetadata.process_block_metadata(core_inst, block)
                else:
                    logger.warn('Failed to verify hash for %s' % block, terminal=True)
    if not exist:
        logger.info('No blocks found to import', terminal=True)