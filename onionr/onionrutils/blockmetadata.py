'''
    Onionr - Private P2P Communication

    Module to fetch block metadata from raw block data and process it
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
import json, sqlite3
import logger, onionrevents
from onionrusers import onionrusers
from etc import onionrvalues
import onionrblockapi
from . import epoch, stringvalidators, bytesconverter
from coredb import dbfiles, blockmetadb
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

def process_block_metadata(blockHash):
    '''
        Read metadata from a block and cache it to the block database
    '''
    curTime = epoch.get_rounded_epoch(roundS=60)
    myBlock = onionrblockapi.Block(blockHash)
    if myBlock.isEncrypted:
        myBlock.decrypt()
    if (myBlock.isEncrypted and myBlock.decrypted) or (not myBlock.isEncrypted):
        blockType = myBlock.getMetadata('type') # we would use myBlock.getType() here, but it is bugged with encrypted blocks

        signer = bytesconverter.bytes_to_str(myBlock.signer)
        valid = myBlock.verifySig()
        if myBlock.getMetadata('newFSKey') is not None:
            onionrusers.OnionrUser(signer).addForwardKey(myBlock.getMetadata('newFSKey'))
            
        try:
            if len(blockType) <= 10:
                blockmetadb.update_block_info(blockHash, 'dataType', blockType)
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
            blockmetadb.update_block_info(blockHash, 'expire', expireTime)
        if not blockType is None:
            blockmetadb.update_block_info(blockHash, 'dataType', blockType)
        #onionrevents.event('processblocks', data = {'block': myBlock, 'type': blockType, 'signer': signer, 'validSig': valid}, onionr = core_inst.onionrInst)
    else:
        pass

def has_block(hash):
    '''
        Check for new block in the list
    '''
    conn = sqlite3.connect(dbfiles.block_meta_db)
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