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
import nacl.signing, nacl.encoding, nacl.public, os

class OnionrCrypto:
    def __init__(self, coreInstance):
        self._core = coreInstance
        self._keyFile = 'data/keys.txt'
        self.pubKey = None
        self.privKey = None

        # Load our own pub/priv Ed25519 keys, gen & save them if they don't exist
        if os.path.exists(self._keyFile):
            with open('data/keys.txt', 'r') as keys:
                keys = keys.read().split(',')
                self.pubKey = keys[0]
                self.privKey = keys[1]
        else:
            keys = self.generatePubKey()
            self.pubKey = keys[0]
            self.privKey = keys[1]
            with open(self._keyFile, 'w') as keyfile:
                keyfile.write(self.pubKey + ',' + self.privKey)
        return

    def pubKeyEncrypt(self, data, peer):
        '''Encrypt to a peers public key (Curve25519, taken from Ed25519 pubkey)'''
        return

    def pubKeyEncrypt(self, data, peer):
        '''pubkey decrypt (Curve25519, taken from Ed25519 pubkey)'''
        return

    def symmetricPeerEncrypt(self, data):
        '''Salsa20 encrypt data to peer (with mac)'''
        return

    def symmetricPeerDecrypt(self, data, peer):
        '''Salsa20 decrypt data from peer (with mac)'''
        return
    
    def generateSymmetric(self, data, peer):
        '''Generate symmetric key'''
        return

    def generatePubKey(self):
        '''Generate a Ed25519 public key pair, return tuple of base64encoded pubkey, privkey'''
        private_key = nacl.signing.SigningKey.generate()
        public_key = private_key.verify_key.encode(encoder=nacl.encoding.Base32Encoder())
        return (public_key.decode(), private_key.encode(encoder=nacl.encoding.Base32Encoder()).decode())