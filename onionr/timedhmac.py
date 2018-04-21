'''
    Onionr - P2P Microblogging Platform & Social network. Run with 'help' for usage.
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

import hmac, base64, time, math

class TimedHMAC:
    def __init__(self, base64Key, data, hashAlgo):
        '''
            base64Key = base64 encoded key
            data = data to hash
            expire = time expiry in epoch
            hashAlgo = string in hashlib.algorithms_available

            Maximum of 10 seconds grace period
        '''
        
        self.data = data
        self.expire = math.floor(time.time())
        self.hashAlgo = hashAlgo
        self.b64Key = base64Key
        generatedHMAC = hmac.HMAC(base64.b64decode(base64Key).decode(), digestmod=self.hashAlgo)
        generatedHMAC.update(data + expire)
        self.HMACResult = generatedHMAC.hexdigest()

        return

    def check(self, data):
        '''
            Check a hash (and verify time is sane)
        '''
        
        testHash = hmac.HMAC(base64.b64decode(base64Key).decode(), digestmod=self.hashAlgo)
        testHash.update(data + math.floor(time.time()))
        testHash = testHash.hexdigest()
        if hmac.compare_digest(testHash, self.HMACResult):
            return true
        
        return false
