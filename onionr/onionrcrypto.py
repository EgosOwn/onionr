'''
    Onionr - Private P2P Communication

    This file handles Onionr's cryptography.
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
import os, binascii, base64, hashlib, time, sys, hmac, secrets
import nacl.signing, nacl.encoding, nacl.public, nacl.hash, nacl.pwhash, nacl.utils, nacl.secret
import logger, onionrproofs
import onionrexceptions, keymanager, core
import config

class OnionrCrypto:
    def __init__(self, coreInstance):
        config.reload()
        self._core = coreInstance
        self._keyFile = self._core.dataDir + 'keys.txt'
        self.pubKey = None
        self.privKey = None
        self.secrets = secrets
        self.deterministicRequirement = 25 # Min deterministic password/phrase length
        self.HASH_ID_ROUNDS = 2000
        self.keyManager = keymanager.KeyManager(self)

        # Load our own pub/priv Ed25519 keys, gen & save them if they don't exist
        if os.path.exists(self._keyFile):
            if len(config.get('general.public_key', '')) > 0:
                self.pubKey = config.get('general.public_key')
            else:
                self.pubKey = self.keyManager.getPubkeyList()[0]
            self.privKey = self.keyManager.getPrivkey(self.pubKey)
        else:
            keys = self.generatePubKey()
            self.pubKey = keys[0]
            self.privKey = keys[1]
            self.keyManager.addKey(self.pubKey, self.privKey)
        return

    def edVerify(self, data, key, sig, encodedData=True):
        '''Verify signed data (combined in nacl) to an ed25519 key'''
        try:
            key = nacl.signing.VerifyKey(key=key, encoder=nacl.encoding.Base32Encoder)
        except nacl.exceptions.ValueError:
            #logger.debug('Signature by unknown key (cannot reverse hash)')
            return False
        except binascii.Error:
            logger.warn('Could not load key for verification, invalid padding')
            return False
        retData = False
        sig = base64.b64decode(sig)
        try:
            data = data.encode()
        except AttributeError:
            pass
        if encodedData:
            try:
                retData = key.verify(data, sig) # .encode() is not the same as nacl.encoding
            except nacl.exceptions.BadSignatureError:
                pass
        else:
            try:
                retData = key.verify(data, sig)
            except nacl.exceptions.BadSignatureError:
                pass
        return retData

    def edSign(self, data, key, encodeResult=False):
        '''Ed25519 sign data'''
        try:
            data = data.encode()
        except AttributeError:
            pass
        key = nacl.signing.SigningKey(seed=key, encoder=nacl.encoding.Base32Encoder)
        retData = ''
        if encodeResult:
            retData = key.sign(data, encoder=nacl.encoding.Base64Encoder).signature.decode() # .encode() is not the same as nacl.encoding
        else:
            retData = key.sign(data).signature
        return retData

    def pubKeyEncrypt(self, data, pubkey, encodedData=False):
        '''Encrypt to a public key (Curve25519, taken from base32 Ed25519 pubkey)'''
        retVal = ''
        box = None
        data = self._core._utils.strToBytes(data)
        
        pubkey = nacl.signing.VerifyKey(pubkey, encoder=nacl.encoding.Base32Encoder()).to_curve25519_public_key()

        if encodedData:
            encoding = nacl.encoding.Base64Encoder
        else:
            encoding = nacl.encoding.RawEncoder
        
        box = nacl.public.SealedBox(pubkey)
        retVal = box.encrypt(data, encoder=encoding)

        return retVal

    def pubKeyDecrypt(self, data, pubkey='', privkey='', encodedData=False):
        '''pubkey decrypt (Curve25519, taken from Ed25519 pubkey)'''
        decrypted = False
        if encodedData:
            encoding = nacl.encoding.Base64Encoder
        else:
            encoding = nacl.encoding.RawEncoder
        if privkey == '':
            privkey = self.privKey
        ownKey = nacl.signing.SigningKey(seed=privkey, encoder=nacl.encoding.Base32Encoder()).to_curve25519_private_key()

        if self._core._utils.validatePubKey(privkey):
            privkey = nacl.signing.SigningKey(seed=privkey, encoder=nacl.encoding.Base32Encoder()).to_curve25519_private_key()
            anonBox = nacl.public.SealedBox(privkey)
        else:
            anonBox = nacl.public.SealedBox(ownKey)
        decrypted = anonBox.decrypt(data, encoder=encoding)
        return decrypted

    def symmetricEncrypt(self, data, key, encodedKey=False, returnEncoded=True):
        '''Encrypt data to a 32-byte key (Salsa20-Poly1305 MAC)'''
        if encodedKey:
            encoding = nacl.encoding.Base64Encoder
        else:
            encoding = nacl.encoding.RawEncoder

        # Make sure data is bytes
        if type(data) != bytes:
            data = data.encode()

        box = nacl.secret.SecretBox(key, encoder=encoding)

        if returnEncoded:
            encoding = nacl.encoding.Base64Encoder
        else:
            encoding = nacl.encoding.RawEncoder

        encrypted = box.encrypt(data, encoder=encoding)
        return encrypted

    def symmetricDecrypt(self, data, key, encodedKey=False, encodedMessage=False, returnEncoded=False):
        '''Decrypt data to a 32-byte key (Salsa20-Poly1305 MAC)'''
        if encodedKey:
            encoding = nacl.encoding.Base64Encoder
        else:
            encoding = nacl.encoding.RawEncoder
        box = nacl.secret.SecretBox(key, encoder=encoding)

        if encodedMessage:
            encoding = nacl.encoding.Base64Encoder
        else:
            encoding = nacl.encoding.RawEncoder
        decrypted = box.decrypt(data, encoder=encoding)
        if returnEncoded:
            decrypted = base64.b64encode(decrypted)
        return decrypted

    def generateSymmetric(self):
        '''Generate a symmetric key (bytes) and return it'''
        return binascii.hexlify(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))

    def generatePubKey(self):
        '''Generate a Ed25519 public key pair, return tuple of base32encoded pubkey, privkey'''
        private_key = nacl.signing.SigningKey.generate()
        public_key = private_key.verify_key.encode(encoder=nacl.encoding.Base32Encoder())
        return (public_key.decode(), private_key.encode(encoder=nacl.encoding.Base32Encoder()).decode())

    def generateDeterministic(self, passphrase, bypassCheck=False):
        '''Generate a Ed25519 public key pair from a password'''
        passStrength = self.deterministicRequirement
        passphrase = self._core._utils.strToBytes(passphrase) # Convert to bytes if not already
        # Validate passphrase length
        if not bypassCheck:
            if len(passphrase) < passStrength:
                raise onionrexceptions.PasswordStrengthError("Passphase must be at least %s characters" % (passStrength,))
        # KDF values
        kdf = nacl.pwhash.argon2id.kdf
        salt = b"U81Q7llrQcdTP0Ux" # Does not need to be unique or secret, but must be 16 bytes
        ops = nacl.pwhash.argon2id.OPSLIMIT_SENSITIVE
        mem = nacl.pwhash.argon2id.MEMLIMIT_SENSITIVE

        key = kdf(32, passphrase, salt, opslimit=ops, memlimit=mem) # Generate seed for ed25519 key
        key = nacl.signing.SigningKey(key)
        return (key.verify_key.encode(nacl.encoding.Base32Encoder).decode(), key.encode(nacl.encoding.Base32Encoder).decode())

    def pubKeyHashID(self, pubkey=''):
        '''Accept a ed25519 public key, return a truncated result of X many sha3_256 hash rounds'''
        if pubkey == '':
            pubkey = self.pubKey
        prev = ''
        pubkey = pubkey.encode()
        for i in range(self.HASH_ID_ROUNDS):
            try:
                prev = prev.encode()
            except AttributeError:
                pass
            hasher = hashlib.sha3_256()
            hasher.update(pubkey + prev)
            prev = hasher.hexdigest()
        result = prev
        return result

    def sha3Hash(self, data):
        try:
            data = data.encode()
        except AttributeError:
            pass
        hasher = hashlib.sha3_256()
        hasher.update(data)
        return hasher.hexdigest()

    def blake2bHash(self, data):
        try:
            data = data.encode()
        except AttributeError:
            pass
        return nacl.hash.blake2b(data)

    def verifyPow(self, blockContent):
        '''
            Verifies the proof of work associated with a block
        '''
        retData = False

        dataLen = len(blockContent)

        try:
            blockContent = blockContent.encode()
        except AttributeError:
            pass

        blockHash = self.sha3Hash(blockContent)
        try:
            blockHash = blockHash.decode() # bytes on some versions for some reason
        except AttributeError:
            pass
        
        difficulty = onionrproofs.getDifficultyForNewBlock(blockContent, ourBlock=False, coreInst=self._core)
        
        if difficulty < int(config.get('general.minimum_block_pow')):
            difficulty = int(config.get('general.minimum_block_pow'))
        mainHash = '0000000000000000000000000000000000000000000000000000000000000000'#nacl.hash.blake2b(nacl.utils.random()).decode()
        puzzle = mainHash[:difficulty]

        if blockHash[:difficulty] == puzzle:
            # logger.debug('Validated block pow')
            retData = True
        else:
            logger.debug("Invalid token, bad proof")

        return retData

    @staticmethod
    def replayTimestampValidation(timestamp):
        if core.Core()._utils.getEpoch() - int(timestamp) > 2419200:
            return False
        else:
            return True

    @staticmethod
    def safeCompare(one, two):
        # Do encode here to avoid spawning core
        try:
            one = one.encode()
        except AttributeError:
            pass
        try:
            two = two.encode()
        except AttributeError:
            pass
        return hmac.compare_digest(one, two)
        
    @staticmethod
    def randomShuffle(theList):
        myList = list(theList)
        shuffledList = []
        myListLength = len(myList) + 1
        while myListLength > 0:
            removed = secrets.randbelow(myListLength)
            try:
                shuffledList.append(myList.pop(removed))
            except IndexError:
                pass
            myListLength = len(myList)
        return shuffledList