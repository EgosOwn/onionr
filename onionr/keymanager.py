'''
    Onionr - P2P Anonymous Storage Network

    Load, save, and delete the user's public key pairs (does not handle peer keys)
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
import onionrcrypto
class KeyManager:
    def __init__(self, crypto):
        assert isinstance(crypto, onionrcrypto.OnionrCrypto)
        self._core = crypto._core
        self._utils = self._core._utils
    
    def getMasterKey(self):
        '''Return the master key (the key created on profile initilization)'''
        return

    def getPubkeyList(self):
        '''Return a list of the user's keys'''
        return
    
    def getPrivkey(self, pubKey):
        return
    
    def changeKey(self, pubKey):
        '''Change crypto.pubKey and crypto.privKey to a given key pair by specifying the public key'''
        return