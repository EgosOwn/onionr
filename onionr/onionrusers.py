'''
    Onionr - P2P Anonymous Storage Network

    Contains abstractions for interacting with users of Onionr
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
import onionrblockapi, logger, onionrexceptions, json
class OnionrUser:
    def __init__(self, coreInst, publicKey):
        self.trust = 0
        self._core = coreInst
        self.publicKey = publicKey

        self.trust = self._core.getPeerInfo(self.publicKey, 'trust')
        return
    
    def setTrust(self, newTrust):
        '''Set the peers trust. 0 = not trusted, 1 = friend, 2 = ultimate'''
        self._core.setPeerInfo(self.publicKey, 'trust', newTrust)

    def isFriend(self):
        if self._core.getPeerInfo(self.publicKey, 'trust') == 1:
            return True
        return False
    
    def getName(self):
        retData = 'anonymous'
        name = self._core.getPeerInfo(self.publicKey, 'name')
        try:
            if len(name) > 0:
                retData = name
        except ValueError:
            pass
        return retData

    def encrypt(self, data):
        encrypted = coreInst._crypto.pubKeyEncrypt(data, self.publicKey, encodedData=True)
        return encrypted
    
    def decrypt(self, data):
        decrypted = coreInst._crypto.pubKeyDecrypt(data, self.publicKey, encodedData=True)
        return decrypted
    
    def forwardEncrypt(self, data):
        return
    
    def forwardDecrypt(self, encrypted):
        return
    
    def findAndSetID(self):
        '''Find any info about the user from existing blocks and cache it to their DB entry'''
        infoBlocks = []
        for bHash in self._core.getBlocksByType('userInfo'):
            block = onionrblockapi.Block(bHash, core=self._core)
            if block.signer == self.publicKey:
                if block.verifySig():
                    newName = block.getMetadata('name')
                    if newName.isalnum():
                        logger.info('%s is now using the name %s.' % (self.publicKey, self._core._utils.escapeAnsi(newName)))
                        self._core.setPeerInfo(self.publicKey, 'name', newName)
            else:
                raise onionrexceptions.InvalidPubkey