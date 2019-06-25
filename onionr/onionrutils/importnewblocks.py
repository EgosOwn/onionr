import glob
import logger, core
from onionrutils import blockmetadata
def import_new_blocks(core_inst=None, scanDir=''):
    '''
        This function is intended to scan for new blocks ON THE DISK and import them
    '''
    if core_inst is None:
        core_inst = core.Core()
    blockList = core_inst.getBlockList()
    exist = False
    if scanDir == '':
        scanDir = core_inst.blockDataLocation
    if not scanDir.endswith('/'):
        scanDir += '/'
    for block in glob.glob(scanDir + "*.dat"):
        if block.replace(scanDir, '').replace('.dat', '') not in blockList:
            exist = True
            logger.info('Found new block on dist %s' % block)
            with open(block, 'rb') as newBlock:
                block = block.replace(scanDir, '').replace('.dat', '')
                if core_inst._crypto.sha3Hash(newBlock.read()) == block.replace('.dat', ''):
                    core_inst.addToBlockDB(block.replace('.dat', ''), dataSaved=True)
                    logger.info('Imported block %s.' % block)
                    blockmetadata.process_block_metadata(block)
                else:
                    logger.warn('Failed to verify hash for %s' % block)
    if not exist:
        logger.info('No blocks found to import')