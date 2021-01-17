"""Onionr - Private P2P Communication.

Create and insert Onionr blocks
"""
from typing import Union
import ujson as json

from gevent import spawn

from onionrutils import bytesconverter, epoch
import filepaths
import onionrstorage
from .. import storagecounter
from onionrplugins import onionrevents as events
from etc import onionrvalues
import config
import onionrcrypto as crypto
import onionrexceptions
from onionrusers import onionrusers
from onionrutils import localcommand, stringvalidators
from .. import blockmetadata
import coredb
from onionrproofs import subprocesspow
import logger
from onionrtypes import UserIDSecretKey
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
storage_counter = storagecounter.StorageCounter()


def _check_upload_queue():
    """
    Return the current upload queue len.

    raises OverflowError if max, false if api not running
    """
    max_upload_queue: int = 5000
    queue = localcommand.local_command('/gethidden', max_wait=10)
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
    Create and insert a block into the network.

    encryptType must be specified to encrypt a block
    if expire is less than date, assumes seconds into future.
        if not assume exact epoch
    """
    our_private_key = crypto.priv_key
    our_pub_key = crypto.pub_key

    allocationReachedMessage = 'Cannot insert block, disk allocation reached.'
    if storage_counter.is_full():
        logger.error(allocationReachedMessage)
        raise onionrexceptions.DiskAllocationReached

    if signing_key != '':
        # if it was specified to use an alternative private key
        our_private_key = signing_key
        our_pub_key = bytesconverter.bytes_to_str(
            crypto.cryptoutils.get_pub_key_from_priv(our_private_key))

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
    with open(filepaths.data_nonce_file, 'a') as nonce_file:
        nonce_file.write(dataNonce + '\n')

    plaintext = data
    plaintextMeta = {}
    plaintextPeer = asymPeer

    retData = ''
    signature = ''
    signer = ''
    metadata = {}

    # metadata is full block metadata
    # meta is internal, user specified metadata

    # only use header if not set in provided meta

    meta['type'] = str(header)

    if encryptType in ('asym', 'sym'):
        metadata['encryptType'] = encryptType
    else:
        if not config.get('general.store_plaintext_blocks', True):
            raise onionrexceptions.InvalidMetadata(
                "Plaintext blocks are disabled, " +
                "yet a plaintext block was being inserted")
        if encryptType not in ('', None):
            raise onionrexceptions.InvalidMetadata(
                'encryptType must be asym or sym, or blank')

    try:
        data = data.encode()
    except AttributeError:
        pass

    if encryptType == 'asym':
        # Duplicate the time in encrypted messages to help prevent replays
        meta['rply'] = createTime
        if sign and asymPeer != our_pub_key:
            try:
                forwardEncrypted = onionrusers.OnionrUser(
                    asymPeer).forwardEncrypt(data)
                data = forwardEncrypted[0]
                meta['forwardEnc'] = True
                # Expire time of key. no sense keeping block after that
                expire = forwardEncrypted[2]
            except onionrexceptions.InvalidPubkey:
                pass
            if not disableForward:
                fsKey = onionrusers.OnionrUser(asymPeer).generateForwardKey()
                meta['newFSKey'] = fsKey
    jsonMeta = json.dumps(meta)
    plaintextMeta = jsonMeta
    if sign:
        signature = crypto.signing.ed_sign(
            jsonMeta.encode() + data, key=our_private_key, encodeResult=True)
        signer = our_pub_key

    if len(jsonMeta) > 1000:
        raise onionrexceptions.InvalidMetadata(
            'meta in json encoded form must not exceed 1000 bytes')

    # encrypt block metadata/sig/content
    if encryptType == 'sym':
        raise NotImplementedError("not yet implemented")
    elif encryptType == 'asym':
        if stringvalidators.validate_pub_key(asymPeer):
            # Encrypt block data with forward secrecy key first, but not meta
            jsonMeta = json.dumps(meta)
            jsonMeta = crypto.encryption.pub_key_encrypt(
                jsonMeta, asymPeer, encodedData=True).decode()
            data = crypto.encryption.pub_key_encrypt(
                data, asymPeer, encodedData=False)
            signature = crypto.encryption.pub_key_encrypt(
                signature, asymPeer, encodedData=True).decode()
            signer = crypto.encryption.pub_key_encrypt(
                signer, asymPeer, encodedData=True).decode()
            try:
                onionrusers.OnionrUser(asymPeer, saveUser=True)
            except ValueError:
                # if peer is already known
                pass
        else:
            logger.warn(f"{asymPeer} is not a valid key to make a block to")
            raise onionrexceptions.InvalidPubkey(
                'tried to make block to invalid key is not a valid base32 encoded ed25519 key')

    # compile metadata
    metadata['meta'] = jsonMeta
    if len(signature) > 0:  # I don't like not pattern
        metadata['sig'] = signature
        metadata['signer'] = signer
    metadata['time'] = createTime

    # ensure expire is integer and of sane length
    if type(expire) is not type(None):  # noqa
        if not len(str(int(expire))) < 20:
            raise ValueError(
                'expire must be valid int less than 20 digits in length')
        # if expire is less than date, assume seconds into future
        if expire < epoch.get_epoch():
            expire = epoch.get_epoch() + expire
        metadata['expire'] = expire

    # send block data (and metadata) to POW module to get tokenized block data
    payload = subprocesspow.SubprocessPOW(data, metadata).start()

    if payload != False:  # noqa
        try:
            retData = onionrstorage.set_data(payload)
        except onionrexceptions.DiskAllocationReached:
            logger.error(allocationReachedMessage)
            retData = False
        else:
            if disableForward:
                logger.warn(
                    f'{retData} asym encrypted block created w/o ephemerality')
            """
            Tell the api server through localCommand to wait for the daemon to
            upload this block to make statistical analysis more difficult
            """
            spawn(
                localcommand.local_command,
                '/daemon-event/upload_event',
                post=True,
                is_json=True,
                post_data={'block': retData}
                ).get(timeout=5)
            coredb.blockmetadb.add.add_to_block_DB(
                retData, selfInsert=True, dataSaved=True)

            if expire is None:
                coredb.blockmetadb.update_block_info(
                    retData, 'expire',
                    createTime + onionrvalues.DEFAULT_EXPIRE)
            else:
                coredb.blockmetadb.update_block_info(retData, 'expire', expire)

            blockmetadata.process_block_metadata(retData)

    if retData != False:  # noqa
        if plaintextPeer == onionrvalues.DENIABLE_PEER_ADDRESS:
            events.event('insertdeniable',
                         {'content': plaintext, 'meta': plaintextMeta,
                          'hash': retData,
                          'peer': bytesconverter.bytes_to_str(asymPeer)},
                         threaded=True)
        else:
            events.event('insertblock',
                         {'content': plaintext, 'meta': plaintextMeta,
                          'hash': retData,
                          'peer': bytesconverter.bytes_to_str(asymPeer)},
                         threaded=True)

    spawn(
        localcommand.local_command,
        '/daemon-event/remove_from_insert_queue_wrapper',
        post=True,
        post_data={'block_hash':
                   bytesconverter.bytes_to_str(
                       crypto.hashers.sha3_hash(data))},
        is_json=True
        ).get(timeout=5)
    return retData
