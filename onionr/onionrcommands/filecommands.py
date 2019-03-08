import base64, sys, os
import logger
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