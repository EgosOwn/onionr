import base64, sys, os
import logger
from onionrblockapi import Block
def add_file(o_inst, singleBlock=False, blockType='bin'):
    '''
        Adds a file to the onionr network
    '''

    if len(sys.argv) >= 3:
        filename = sys.argv[2]
        contents = None

        if not os.path.exists(filename):
            logger.error('That file does not exist. Improper path (specify full path)?')
            return
        logger.info('Adding file... this might take a long time.')
        try:
            with open(filename, 'rb') as singleFile:
                blockhash = o_inst.onionrCore.insertBlock(base64.b64encode(singleFile.read()), header=blockType)
            if len(blockhash) > 0:
                logger.info('File %s saved in block %s' % (filename, blockhash))
        except:
            logger.error('Failed to save file in block.', timestamp = False)
    else:
        logger.error('%s add-file <filename>' % sys.argv[0], timestamp = False)

def getFile(o_inst):
    '''
        Get a file from onionr blocks
    '''
    try:
        fileName = sys.argv[2]
        bHash = sys.argv[3]
    except IndexError:
        logger.error("Syntax %s %s" % (sys.argv[0], '/path/to/filename <blockhash>'))
    else:
        logger.info(fileName)

        contents = None
        if os.path.exists(fileName):
            logger.error("File already exists")
            return
        if not o_inst.onionrUtils.validateHash(bHash):
            logger.error('Block hash is invalid')
            return

        with open(fileName, 'wb') as myFile:
            myFile.write(base64.b64decode(Block(bHash, core=o_inst.onionrCore).bcontent))
    return