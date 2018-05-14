'''
    Onionr - P2P Microblogging Platform & Social network

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
import nacl.signing, nacl.encoding, nacl.public, nacl.hash, nacl.secret, os, binascii, base64, hashlib, logger, onionrproofs, time, math

class OnionrCrypto:
    def __init__(self, coreInstance):
        self._core = coreInstance
        self._keyFile = 'data/keys.txt'
        self.keyPowFile = 'data/keyPow.txt'
        self.pubKey = None
        self.privKey = None

        self.pubKeyPowToken = None
        self.pubKeyPowHash = None

        self.HASH_ID_ROUNDS = 2000

        # Load our own pub/priv Ed25519 keys, gen & save them if they don't exist
        if os.path.exists(self._keyFile):
            with open('data/keys.txt', 'r') as keys:
                keys = keys.read().split(',')
                self.pubKey = keys[0]
                self.privKey = keys[1]
            try:
                with open(self.keyPowFile, 'r') as powFile:
                    data = powFile.read()
                    self.pubKeyPowHash = data.split('-')[0]
                    self.pubKeyPowToken = data.split('-')[1]
            except (FileNotFoundError, IndexError):
                pass
        else:
            keys = self.generatePubKey()
            self.pubKey = keys[0]
            self.privKey = keys[1]
            with open(self._keyFile, 'w') as keyfile:
                keyfile.write(self.pubKey + ',' + self.privKey)
            with open(self.keyPowFile, 'w') as keyPowFile:
                proof = onionrproofs.POW(self.pubKey)
                logger.info('Doing necessary work to insert our public key')
                while True:
                    time.sleep(0.2)
                    powToken = proof.getResult()
                    if powToken != False:
                        break
                keyPowFile.write(base64.b64encode(powToken[1]).decode())
                self.pubKeyPowToken = powToken[1]
                self.pubKeyPowHash = powToken[0]
        return

    def edVerify(self, data, key, sig, encodedData=True):
        '''Verify signed data (combined in nacl) to an ed25519 key'''
        try:
            key = nacl.signing.VerifyKey(key=key, encoder=nacl.encoding.Base32Encoder)
        except nacl.exceptions.ValueError:
            logger.warn('Signature by unknown key (cannot reverse hash)')
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

    def pubKeyEncrypt(self, data, pubkey, anonymous=False, encodedData=False):
        '''Encrypt to a public key (Curve25519, taken from base32 Ed25519 pubkey)'''
        retVal = ''

        if encodedData:
            encoding = nacl.encoding.Base64Encoder
        else:
            encoding = nacl.encoding.RawEncoder

        if self.privKey != None and not anonymous:
            ownKey = nacl.signing.SigningKey(seed=self.privKey, encoder=nacl.encoding.Base32Encoder)
            key = nacl.signing.VerifyKey(key=pubkey, encoder=nacl.encoding.Base32Encoder).to_curve25519_public_key()
            ourBox = nacl.public.Box(ownKey, key)
            retVal = ourBox.encrypt(data.encode(), encoder=encoding)
        elif anonymous:
            key = nacl.signing.VerifyKey(key=pubkey, encoder=nacl.encoding.Base32Encoder).to_curve25519_public_key()
            anonBox = nacl.public.SealedBox(key)
            retVal = anonBox.encrypt(data.encode(), encoder=encoding)
        return retVal

    def pubKeyDecrypt(self, data, pubkey='', anonymous=False, encodedData=False):
        '''pubkey decrypt (Curve25519, taken from Ed25519 pubkey)'''
        retVal = False
        if encodedData:
            encoding = nacl.encoding.Base64Encoder
        else:
            encoding = nacl.encoding.RawEncoder
        ownKey = nacl.signing.SigningKey(seed=self.privKey, encoder=nacl.encoding.Base32Encoder()).to_curve25519_private_key()
        if self.privKey != None and not anonymous:
            ourBox = nacl.public.Box(ownKey, pubkey)
            decrypted = ourBox.decrypt(data, encoder=encoding)
        elif anonymous:
            anonBox = nacl.public.SealedBox(ownKey)
            decrypted = anonBox.decrypt(data, encoder=encoding)
        return decrypted

    def symmetricPeerEncrypt(self, data, peer):
        '''Salsa20 encrypt data to peer (with mac)
            this function does not accept a key, it is a wrapper for encryption with a peer
        '''
        key = self._core.getPeerInfo(4)
        if type(key) != bytes:
            key = self._core.getPeerInfo(2)
        encrypted = self.symmetricEncrypt(data, key, encodedKey=True)
        return encrypted

    def symmetricPeerDecrypt(self, data, peer):
        '''Salsa20 decrypt data from peer (with mac)
        this function does not accept a key, it is a wrapper for encryption with a peer
        '''
        key = self._core.getPeerInfo(4)
        if type(key) != bytes:
            key = self._core.getPeerInfo(2)
        decrypted = self.symmetricDecrypt(data, key, encodedKey=True)
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

    def generateSymmetricPeer(self, peer):
        '''Generate symmetric key for a peer and save it to the peer database'''
        key = self.generateSymmetric()
        self._core.setPeerInfo(peer, 'forwardKey', key)
        return

    def generateSymmetric(self):
        '''Generate a symmetric key (bytes) and return it'''
        return binascii.hexlify(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))

    def generatePubKey(self):
        '''Generate a Ed25519 public key pair, return tuple of base32encoded pubkey, privkey'''
        private_key = nacl.signing.SigningKey.generate()
        public_key = private_key.verify_key.encode(encoder=nacl.encoding.Base32Encoder())
        return (public_key.decode(), private_key.encode(encoder=nacl.encoding.Base32Encoder()).decode())

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
        hasher = hashlib.sha3_256()
        hasher.update(data)
        return hasher.hexdigest()

    def blake2bHash(self, data):
        try:
            data = data.encode()
        except AttributeError:
            pass
        return nacl.hash.blake2b(data)

    def verifyPow(self, blockContent, metadata):
        '''
            Verifies the proof of work associated with a block
        '''
        retData = False

        if not (('powToken' in metadata) and ('powHash' in metadata)):
            return False

        dataLen = len(blockContent)

        expectedHash = self.blake2bHash(base64.b64decode(metadata['powToken']) + self.blake2bHash(blockContent.encode()))
        difficulty = 0
        try:
            expectedHash = expectedHash.decode()
        except AttributeError:
            pass
        if metadata['powHash'] == expectedHash:
            difficulty = math.floor(dataLen / 1000000)

            mainHash = '0000000000000000000000000000000000000000000000000000000000000000'#nacl.hash.blake2b(nacl.utils.random()).decode()
            puzzle = mainHash[:difficulty]

            if metadata['powHash'][:difficulty] == puzzle:
                # logger.debug('Validated block pow')
                retData = True
            else:
                logger.debug("Invalid token (#1)")
        else:
            logger.debug('Invalid token (#2): Expected hash %s, got hash %s...' % (metadata['powHash'], expectedHash))

        return retData
