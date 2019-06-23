import json
import logger, onionrevents
from onionrusers import onionrusers
from etc import onionrvalues
from onionrblockapi import Block
def get_block_metadata_from_data(utils_inst, blockData):
    '''
        accepts block contents as string, returns a tuple of 
        metadata, meta (meta being internal metadata, which will be 
        returned as an encrypted base64 string if it is encrypted, dict if not).
    '''
    meta = {}
    metadata = {}
    data = blockData
    try:
        blockData = blockData.encode()
    except AttributeError:
        pass

    try:
        metadata = json.loads(blockData[:blockData.find(b'\n')].decode())
    except json.decoder.JSONDecodeError:
        pass
    else:
        data = blockData[blockData.find(b'\n'):].decode()

        if not metadata['encryptType'] in ('asym', 'sym'):
            try:
                meta = json.loads(metadata['meta'])
            except KeyError:
                pass
        meta = metadata['meta']
    return (metadata, meta, data)

def process_block_metadata(utils_inst, blockHash):
    '''
        Read metadata from a block and cache it to the block database
    '''
    curTime = utils_inst.getRoundedEpoch(roundS=60)
    myBlock = Block(blockHash, utils_inst._core)
    if myBlock.isEncrypted:
        myBlock.decrypt()
    if (myBlock.isEncrypted and myBlock.decrypted) or (not myBlock.isEncrypted):
        blockType = myBlock.getMetadata('type') # we would use myBlock.getType() here, but it is bugged with encrypted blocks
        signer = utils_inst.bytesToStr(myBlock.signer)
        valid = myBlock.verifySig()
        if myBlock.getMetadata('newFSKey') is not None:
            onionrusers.OnionrUser(utils_inst._core, signer).addForwardKey(myBlock.getMetadata('newFSKey'))
            
        try:
            if len(blockType) <= 10:
                utils_inst._core.updateBlockInfo(blockHash, 'dataType', blockType)
        except TypeError:
            logger.warn("Missing block information")
            pass
        # Set block expire time if specified
        try:
            expireTime = myBlock.getHeader('expire')
            assert len(str(int(expireTime))) < 20 # test that expire time is an integer of sane length (for epoch)
        except (AssertionError, ValueError, TypeError) as e:
            expireTime = onionrvalues.OnionrValues().default_expire + curTime
        finally:
            utils_inst._core.updateBlockInfo(blockHash, 'expire', expireTime)
        if not blockType is None:
            utils_inst._core.updateBlockInfo(blockHash, 'dataType', blockType)
        onionrevents.event('processblocks', data = {'block': myBlock, 'type': blockType, 'signer': signer, 'validSig': valid}, onionr = utils_inst._core.onionrInst)
    else:
        pass