import json, sqlite3
import logger, onionrevents
from onionrusers import onionrusers
from etc import onionrvalues
import onionrblockapi
from . import epoch, stringvalidators, bytesconverter
def get_block_metadata_from_data(blockData):
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

def process_block_metadata(core_inst, blockHash):
    '''
        Read metadata from a block and cache it to the block database
    '''
    curTime = epoch.get_rounded_epoch(roundS=60)
    myBlock = onionrblockapi.Block(blockHash, core_inst)
    if myBlock.isEncrypted:
        myBlock.decrypt()
    if (myBlock.isEncrypted and myBlock.decrypted) or (not myBlock.isEncrypted):
        blockType = myBlock.getMetadata('type') # we would use myBlock.getType() here, but it is bugged with encrypted blocks
        print('blockType', blockType)
        signer = bytesconverter.bytes_to_str(myBlock.signer)
        valid = myBlock.verifySig()
        if myBlock.getMetadata('newFSKey') is not None:
            onionrusers.OnionrUser(core_inst, signer).addForwardKey(myBlock.getMetadata('newFSKey'))
            
        try:
            if len(blockType) <= 10:
                core_inst.updateBlockInfo(blockHash, 'dataType', blockType)
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
            core_inst.updateBlockInfo(blockHash, 'expire', expireTime)
        if not blockType is None:
            core_inst.updateBlockInfo(blockHash, 'dataType', blockType)
        onionrevents.event('processblocks', data = {'block': myBlock, 'type': blockType, 'signer': signer, 'validSig': valid}, onionr = core_inst.onionrInst)
    else:
        pass

def has_block(core_inst, hash):
    '''
        Check for new block in the list
    '''
    conn = sqlite3.connect(core_inst.blockDB)
    c = conn.cursor()
    if not stringvalidators.validate_hash(hash):
        raise Exception("Invalid hash")
    for result in c.execute("SELECT COUNT() FROM hashes WHERE hash = ?", (hash,)):
        if result[0] >= 1:
            conn.commit()
            conn.close()
            return True
        else:
            conn.commit()
            conn.close()
            return False
    return False