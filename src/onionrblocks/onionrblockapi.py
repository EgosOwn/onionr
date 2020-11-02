"""Onionr - P2P Anonymous Storage Network.

OnionrBlocks class for abstraction of blocks
"""
import datetime
import onionrstorage

import unpaddedbase32
import ujson as json
import nacl.exceptions

import logger
import onionrexceptions
from onionrusers import onionrusers
from onionrutils import stringvalidators, epoch
from coredb import blockmetadb
from onionrutils import bytesconverter
import onionrblocks
from onionrcrypto import encryption, cryptoutils as cryptoutils, signing
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


class Block:
    blockCacheOrder = list() # NEVER write your own code that writes to this!
    blockCache = dict() # should never be accessed directly, look at Block.getCache()

    def __init__(self, hash = None, type = None, content = None, expire=None, decrypt=False, bypassReplayCheck=False):
        # take from arguments
        # sometimes people input a bytes object instead of str in `hash`
        if (not hash is None) and isinstance(hash, bytes):
            hash = hash.decode()

        self.hash = hash
        self.btype = type
        self.bcontent = content
        self.expire = expire
        self.bypassReplayCheck = bypassReplayCheck

        # initialize variables
        self.valid = True
        self.raw = None
        self.signed = False
        self.signature = None
        self.signedData = None
        self.blockFile = None
        self.bheader = {}
        self.bmetadata = {}
        self.isEncrypted = False
        self.decrypted = False
        self.signer = None
        self.validSig = False
        self.autoDecrypt = decrypt
        self.claimedTime = None

        self.update()

    def decrypt(self, encodedData = True):
        """
            Decrypt a block, loading decrypted data into their vars
        """

        if self.decrypted:
            return True
        retData = False
        # decrypt data
        if self.getHeader('encryptType') == 'asym':
            try:
                self.bcontent = encryption.pub_key_decrypt(self.bcontent, encodedData=False)

                bmeta = encryption.pub_key_decrypt(self.bmetadata, encodedData=encodedData)

                try:
                    bmeta = bmeta.decode()
                except AttributeError:
                    # yet another bytes fix
                    pass
                self.bmetadata = json.loads(bmeta)
                self.signature = encryption.pub_key_decrypt(self.signature, encodedData=encodedData)

                self.signer = encryption.pub_key_decrypt(self.signer, encodedData=encodedData)

                self.bheader['signer'] = self.signer.decode()
                self.signedData = json.dumps(self.bmetadata).encode() + self.bcontent

                if not self.signer is None:
                    if not self.verifySig():
                        raise onionrexceptions.SignatureError("Block has invalid signature")

                # Check for replay attacks
                try:
                    if epoch.get_epoch() - blockmetadb.get_block_date(self.hash) > 60:
                        if not cryptoutils.replay_validator(self.bmetadata['rply']): raise onionrexceptions.ReplayAttack
                except (AssertionError, KeyError, TypeError, onionrexceptions.ReplayAttack) as e:
                    if not self.bypassReplayCheck:
                        # Zero out variables to prevent reading of replays
                        self.bmetadata = {}
                        self.signer = ''
                        self.bheader['signer'] = ''
                        self.signedData = ''
                        self.signature = ''
                        raise onionrexceptions.ReplayAttack('Signature is too old. possible replay attack')
                try:
                    if not self.bmetadata['forwardEnc']: raise KeyError
                except (AssertionError, KeyError) as e:
                    pass
                else:
                    try:
                        self.bcontent = onionrusers.OnionrUser(self.signer).forwardDecrypt(self.bcontent)
                    except (onionrexceptions.DecryptionError, nacl.exceptions.CryptoError) as e:
                        logger.error(str(e))
                        pass
            except (nacl.exceptions.CryptoError,) as e:
                logger.debug(f'Could not decrypt block. encodedData: {encodedData}. Either invalid key or corrupted data ' + str(e))
            except onionrexceptions.ReplayAttack:
                logger.warn('%s is possibly a replay attack' % (self.hash,))
            else:
                retData = True
                self.decrypted = True
        return retData

    def verifySig(self):
        """
            Verify if a block's signature is signed by its claimed signer
        """
        if self.signer is None:
            return False
        if signing.ed_verify(data=self.signedData, key=self.signer, sig=self.signature, encodedData=True):
            self.validSig = True
        else:
            self.validSig = False
        return self.validSig

    def update(self, data = None, file = None):
        """
            Loads data from a block in to the current object.

            Inputs:
            - data (str):
              - if None: will load from file by hash
              - else: will load from `data` string
            - file (str):
              - if None: will load from file specified in this parameter
              - else: will load from wherever block is stored by hash

            Outputs:
            - (bool): indicates whether or not the operation was successful
        """
        try:
            # import from string
            blockdata = data

            # import from file
            if blockdata is None:
                try:
                    blockdata = onionrstorage.getData(self.getHash())#.decode()
                except AttributeError:
                    raise onionrexceptions.NoDataAvailable('Block does not exist')
            else:
                self.blockFile = None
            # parse block
            self.raw = blockdata
            self.bheader = json.loads(self.getRaw()[:self.getRaw().index(b'\n')])
            self.bcontent = self.getRaw()[self.getRaw().index(b'\n') + 1:]
            if ('encryptType' in self.bheader) and (self.bheader['encryptType'] in ('asym', 'sym')):
                self.bmetadata = self.getHeader('meta', None)
                self.isEncrypted = True
            else:
                self.bmetadata = json.loads(self.getHeader('meta', None))
            self.btype = self.getMetadata('type', None)
            self.signed = ('sig' in self.getHeader() and self.getHeader('sig') != '')
            # TODO: detect if signer is hash of pubkey or not
            self.signer = self.getHeader('signer', None)
            self.signature = self.getHeader('sig', None)
            # signed data is jsonMeta + block content (no linebreak)
            self.signedData = (None if not self.isSigned() else self.getHeader('meta').encode() + self.getContent())
            self.date = blockmetadb.get_block_date(self.getHash())
            self.claimedTime = self.getHeader('time', None)

            if not self.getDate() is None:
                self.date = datetime.datetime.fromtimestamp(self.getDate())

            self.valid = True

            if self.autoDecrypt:
                self.decrypt()

            return True
        except Exception as e:
            logger.warn('Failed to parse block %s' % self.getHash(), error = e, timestamp = False)


        self.valid = False
        return False


    # getters

    def getExpire(self):
        """
            Returns the expire time for a block

            Outputs:
            - (int): the expire time for a block, or None
        """
        return self.expire

    def getHash(self):
        """
            Returns the hash of the block if saved to file

            Outputs:
            - (str): the hash of the block, or None
        """

        return self.hash

    def getType(self):
        """
            Returns the type of the block

            Outputs:
            - (str): the type of the block
        """
        return self.btype

    def getRaw(self):
        """
            Returns the raw contents of the block, if saved to file

            Outputs:
            - (bytes): the raw contents of the block, or None
        """

        return self.raw

    def getHeader(self, key = None, default = None):
        """
            Returns the header information

            Inputs:
            - key (str): only returns the value of the key in the header

            Outputs:
            - (dict/str): either the whole header as a dict, or one value
        """

        if not key is None:
            if key in self.getHeader():
                return self.getHeader()[key]
            return default
        return self.bheader

    def getMetadata(self, key = None, default = None):
        """
            Returns the metadata information

            Inputs:
            - key (str): only returns the value of the key in the metadata

            Outputs:
            - (dict/str): either the whole metadata as a dict, or one value
        """

        if not key is None:
            if key in self.getMetadata():
                return self.getMetadata()[key]
            return default
        return self.bmetadata

    def getContent(self):
        """
            Returns the contents of the block

            Outputs:
            - (str): the contents of the block
        """

        return self.bcontent

    def getDate(self):
        """
            Returns the date that the block was received, if loaded from file

            Outputs:
            - (datetime): the date that the block was received
        """

        return self.date

    def getBlockFile(self):
        """
            Returns the location of the block file if it is saved

            Outputs:
            - (str): the location of the block file, or None
        """

        return self.blockFile

    def isValid(self):
        """
            Checks if the block is valid

            Outputs:
            - (bool): whether or not the block is valid
        """

        return self.valid

    def isSigned(self):
        """
            Checks if the block was signed

            Outputs:
            - (bool): whether or not the block is signed
        """

        return self.signed

    def getSignature(self):
        """
            Returns the base64-encoded signature

            Outputs:
            - (str): the signature, or None
        """

        return self.signature

    def getSignedData(self):
        """
            Returns the data that was signed

            Outputs:
            - (str): the data that was signed, or None
        """

        return self.signedData

    def isSigner(self, signer, encodedData = True):
        """
            Checks if the block was signed by the signer inputted

            Inputs:
            - signer (str): the public key of the signer to check against
            - encodedData (bool): whether or not the `signer` argument is base64 encoded

            Outputs:
            - (bool): whether or not the signer of the block is the signer inputted
        """
        signer = unpaddedbase32.repad(bytesconverter.str_to_bytes(signer))
        try:
            if (not self.isSigned()) or (not stringvalidators.validate_pub_key(signer)):
                return False

            return bool(signing.ed_verify(self.getSignedData(), signer, self.getSignature(), encodedData = encodedData))
        except:
            return False

    # setters

    def setType(self, btype):
        """
            Sets the type of the block

            Inputs:
            - btype (str): the type of block to be set to

            Outputs:
            - (Block): the Block instance
        """

        self.btype = btype
        return self

    def setMetadata(self, key, val):
        """
            Sets a custom metadata value

            Metadata should not store block-specific data structures.

            Inputs:
            - key (str): the key
            - val: the value (type is irrelevant)

            Outputs:
            - (Block): the Block instance
        """

        self.bmetadata[key] = val
        return self

    def setContent(self, bcontent):
        """
            Sets the contents of the block

            Inputs:
            - bcontent (str): the contents to be set to

            Outputs:
            - (Block): the Block instance
        """

        self.bcontent = str(bcontent)
        return self

    # static functions
    def exists(bHash):
        """
            Checks if a block is saved to file or not

            Inputs:
            - hash (str/Block):
              - if (Block): check if this block is saved to file
              - if (str): check if a block by this hash is in file

            Outputs:
            - (bool): whether or not the block file exists
        """

        # no input data? scrap it.
        if bHash is None:
            return False

        if isinstance(bHash, Block):
            bHash = bHash.getHash()

        ret = isinstance(onionrstorage.getData(bHash), type(None))

        return not ret
