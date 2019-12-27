"""
    Onionr - Private P2P Communication

    Create and insert Onionr blocks
"""
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
from typing import Union
import json

from onionrutils import bytesconverter, epoch
import filepaths, onionrstorage
from .. import storagecounter
from onionrplugins import onionrevents as events
from etc import powchoice, onionrvalues
import config, onionrcrypto as crypto, onionrexceptions
from onionrusers import onionrusers
from onionrutils import localcommand, blockmetadata, stringvalidators
import coredb
import onionrproofs
from onionrproofs import subprocesspow
import logger
from onionrtypes import UserIDSecretKey


def _check_upload_queue():
    """Returns the current upload queue len
    raises OverflowError if max, false if api not running
    """
    max_upload_queue: int = 5000
    queue = localcommand.local_command('/gethidden', maxWait=10)
    up_queue = False

    try:
        up_queue = len(queue.splitlines())
    except AttributeError:
        pass
    else:
        if up_queue >= max_upload_queue:
            raise OverflowError
    return up_queue


def insert_block(data: Union[str, bytes], header: str = 'txt',
                 sign: bool = False, encryptType: str = '', symKey: str = '',
                 asymPeer: str = '', meta: dict = {},
                 expire: Union[int, None] = None, disableForward: bool = False,
                 signing_key: UserIDSecretKey = '') -> Union[str, bool]:
    """
        Inserts a block into the network
        encryptType must be specified to encrypt a block
    """
    our_private_key = crypto.priv_key
    our_pub_key = crypto.pub_key

    is_offline = True

    storage_counter = storagecounter.StorageCounter()

    allocationReachedMessage = 'Cannot insert block, disk allocation reached.'
    if storage_counter.is_full():
        logger.error(allocationReachedMessage)
        raise onionrexceptions.DiskAllocationReached

    if not _check_upload_queue() is False: is_offline = False

    if signing_key != '':
        # if it was specified to use an alternative private key
        our_private_key = signing_key
        our_pub_key = bytesconverter.bytes_to_str(crypto.cryptoutils.get_pub_key_from_priv(our_private_key))

    use_subprocess = powchoice.use_subprocess(config)

    retData = False

    if type(data) is None:
        raise ValueError('Data cannot be none')

    createTime = epoch.get_epoch()

    dataNonce = bytesconverter.bytes_to_str(crypto.hashers.sha3_hash(data))
    try:
        with open(filepaths.data_nonce_file, 'r') as nonces:
            if dataNonce in nonces:
                return retData
    except FileNotFoundError:
        pass
    # record nonce
    with open(filepaths.data_nonce_file, 'a') as nonceFile:
        nonceFile.write(dataNonce + '\n')

    plaintext = data
    plaintextMeta = {}
    plaintextPeer = asymPeer

    retData = ''
    signature = ''
    signer = ''
    metadata = {}

    # metadata is full block metadata, meta is internal, user specified metadata

    # only use header if not set in provided meta

    meta['type'] = str(header)

    if encryptType in ('asym', 'sym'):
        metadata['encryptType'] = encryptType
    else:
        if not config.get('general.store_plaintext_blocks', True): raise onionrexceptions.InvalidMetadata("Plaintext blocks are disabled, yet a plaintext block was being inserted")
        if not encryptType in ('', None):
            raise onionrexceptions.InvalidMetadata('encryptType must be asym or sym, or blank')

    try:
        data = data.encode()
    except AttributeError:
        pass

    if encryptType == 'asym':
        meta['rply'] = createTime # Duplicate the time in encrypted messages to prevent replays
        if not disableForward and sign and asymPeer != our_pub_key:
            try:
                forwardEncrypted = onionrusers.OnionrUser(asymPeer).forwardEncrypt(data)
                data = forwardEncrypted[0]
                meta['forwardEnc'] = True
                expire = forwardEncrypted[2] # Expire time of key. no sense keeping block after that
            except onionrexceptions.InvalidPubkey:
                pass
                #onionrusers.OnionrUser(self, asymPeer).generateForwardKey()
            fsKey = onionrusers.OnionrUser(asymPeer).generateForwardKey()
            #fsKey = onionrusers.OnionrUser(self, asymPeer).getGeneratedForwardKeys().reverse()
            meta['newFSKey'] = fsKey
    jsonMeta = json.dumps(meta)
    plaintextMeta = jsonMeta
    if sign:
        signature = crypto.signing.ed_sign(jsonMeta.encode() + data, key=our_private_key, encodeResult=True)
        signer = our_pub_key

    if len(jsonMeta) > 1000:
        raise onionrexceptions.InvalidMetadata('meta in json encoded form must not exceed 1000 bytes')

    # encrypt block metadata/sig/content
    if encryptType == 'sym':
        raise NotImplementedError("not yet implemented")
    elif encryptType == 'asym':
        if stringvalidators.validate_pub_key(asymPeer):
            # Encrypt block data with forward secrecy key first, but not meta
            jsonMeta = json.dumps(meta)
            jsonMeta = crypto.encryption.pub_key_encrypt(jsonMeta, asymPeer, encodedData=True).decode()
            data = crypto.encryption.pub_key_encrypt(data, asymPeer, encodedData=False)#.decode()
            signature = crypto.encryption.pub_key_encrypt(signature, asymPeer, encodedData=True).decode()
            signer = crypto.encryption.pub_key_encrypt(signer, asymPeer, encodedData=True).decode()
            try:
                onionrusers.OnionrUser(asymPeer, saveUser=True)
            except ValueError:
                # if peer is already known
                pass
        else:
            raise onionrexceptions.InvalidPubkey(asymPeer + ' is not a valid base32 encoded ed25519 key')

    # compile metadata
    metadata['meta'] = jsonMeta
    if len(signature) > 0:  # I don't like not pattern
        metadata['sig'] = signature
        metadata['signer'] = signer
    metadata['time'] = createTime

    # ensure expire is integer and of sane length
    if type(expire) is not type(None):
        if not len(str(int(expire))) < 20: raise ValueError('expire must be valid int less than 20 digits in length')
        metadata['expire'] = expire

    # send block data (and metadata) to POW module to get tokenized block data
    if use_subprocess:
        payload = subprocesspow.SubprocessPOW(data, metadata).start()
    else:
        payload = onionrproofs.POW(metadata, data).waitForResult()
    if payload != False:
        try:
            retData = onionrstorage.set_data(payload)
        except onionrexceptions.DiskAllocationReached:
            logger.error(allocationReachedMessage)
            retData = False
        else:
            # Tell the api server through localCommand to wait for the daemon to upload this block to make statistical analysis more difficult
            coredb.daemonqueue.daemon_queue_add('uploadEvent', retData)
            coredb.blockmetadb.add.add_to_block_DB(retData, selfInsert=True, dataSaved=True)

            if expire is None:
                coredb.blockmetadb.update_block_info(retData, 'expire',
                                                     createTime + onionrvalues.DEFAULT_EXPIRE)
            else:
                coredb.blockmetadb.update_block_info(retData, 'expire', expire)

            blockmetadata.process_block_metadata(retData)

    if retData != False:
        if plaintextPeer == onionrvalues.DENIABLE_PEER_ADDRESS:
            events.event('insertdeniable', {'content': plaintext, 'meta': plaintextMeta, 'hash': retData, 'peer': bytesconverter.bytes_to_str(asymPeer)}, threaded = True)
        else:
            events.event('insertblock', {'content': plaintext, 'meta': plaintextMeta, 'hash': retData, 'peer': bytesconverter.bytes_to_str(asymPeer)}, threaded = True)
    coredb.daemonqueue.daemon_queue_add('remove_from_insert_list', data= dataNonce)
    return retData
