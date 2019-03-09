import sys
import logger

def add_peer(o_inst):
    try:
        newPeer = sys.argv[2]
    except:
        pass
    else:
        if o_inst.onionrUtils.hasKey(newPeer):
            logger.info('We already have that key')
            return
        logger.info("Adding peer: " + logger.colors.underline + newPeer)
        try:
            if o_inst.onionrCore.addPeer(newPeer):
                logger.info('Successfully added key')
        except AssertionError:
            logger.error('Failed to add key')

def add_address(o_inst):
    try:
        newAddress = sys.argv[2]
        newAddress = newAddress.replace('http:', '').replace('/', '')
    except:
        pass
    else:
        logger.info("Adding address: " + logger.colors.underline + newAddress)
        if self.onionrCore.addAddress(newAddress):
            logger.info("Successfully added address.")
        else:
            logger.warn("Unable to add address.")