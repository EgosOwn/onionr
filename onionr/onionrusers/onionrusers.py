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
import onionrblockapi, logger, onionrexceptions, json, sqlite3, time
import nacl.exceptions

def deleteExpiredKeys(coreInst):
    # Fetch the keys we generated for the peer, that are still around
    conn = sqlite3.connect(coreInst.forwardKeysFile, timeout=10)
    c = conn.cursor()

    curTime = coreInst._utils.getEpoch()
    c.execute("DELETE from myForwardKeys where expire <= ?", (curTime,))
    conn.commit()
    conn.execute("VACUUM")
    conn.close()
    return

def deleteTheirExpiredKeys(coreInst, pubkey):
    conn = sqlite3.connect(self._core.peerDB, timeout=10)
    c = conn.cursor()

    # Prepare the insert
    command = (pubkey, coreInst._utils.getEpoch())

    c.execute("DELETE from forwardKeys where peerKey = ? and expire <= ?", command)

    conn.commit()
    conn.close()

DEFAULT_KEY_EXPIRE = 604800
#DEFAULT_KEY_EXPIRE = 600

class OnionrUser:
    def __init__(self, coreInst, publicKey, saveUser=False):
        '''
            OnionrUser is an abstraction for "users" of the network. 
            
            Takes an instance of onionr core, a base32 encoded ed25519 public key, and a bool saveUser
            saveUser determines if we should add a user to our peer database or not.
        '''
        if ' ' in coreInst._utils.bytesToStr(publicKey).strip():
            publicKey = coreInst._utils.convertHumanReadableID(publicKey)

        self.trust = 0
        self._core = coreInst
        self.publicKey = publicKey

        if saveUser:
            try:
                self._core.addPeer(publicKey)
            except AssertionError:
                pass

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
        encrypted = self._core._crypto.pubKeyEncrypt(data, self.publicKey, encodedData=True)
        return encrypted

    def decrypt(self, data):
        decrypted = self._core._crypto.pubKeyDecrypt(data, self.publicKey, encodedData=True)
        return decrypted

    def forwardEncrypt(self, data):
        deleteExpiredKeys(self._core)
        retData = ''
        forwardKey = self._getLatestForwardKey()
        if self._core._utils.validatePubKey(forwardKey[0]):
            retData = self._core._crypto.pubKeyEncrypt(data, forwardKey[0], encodedData=True)
        else:
            raise onionrexceptions.InvalidPubkey("No valid forward secrecy key available for this user")
        #self.generateForwardKey()
        return (retData, forwardKey[0], forwardKey[1])

    def forwardDecrypt(self, encrypted):
        retData = ""
        for key in self.getGeneratedForwardKeys(False):
            try:
                retData = self._core._crypto.pubKeyDecrypt(encrypted, privkey=key[1], encodedData=True)
            except nacl.exceptions.CryptoError:
                retData = False
            else:
                break
        else:
            raise onionrexceptions.DecryptionError("Could not decrypt forward secrecy content")
        return retData

    def _getLatestForwardKey(self):
        # Get the latest forward secrecy key for a peer
        key = ""
        conn = sqlite3.connect(self._core.peerDB, timeout=10)
        c = conn.cursor()

        # TODO: account for keys created at the same time (same epoch)
        for row in c.execute("SELECT forwardKey, max(DATE) FROM forwardKeys WHERE peerKey = ?", (self.publicKey,)):
            key = (row[0], row[1])
            break

        conn.commit()
        conn.close()

        return key

    def _getForwardKeys(self):
        conn = sqlite3.connect(self._core.peerDB, timeout=10)
        c = conn.cursor()
        keyList = []

        for row in c.execute("SELECT forwardKey, date FROM forwardKeys WHERE peerKey = ? ORDER BY date DESC", (self.publicKey,)):
            keyList.append((row[0], row[1]))

        conn.commit()
        conn.close()

        return list(keyList)

    def generateForwardKey(self, expire=DEFAULT_KEY_EXPIRE):

        # Generate a forward secrecy key for the peer
        conn = sqlite3.connect(self._core.forwardKeysFile, timeout=10)
        c = conn.cursor()
        # Prepare the insert
        time = self._core._utils.getEpoch()
        newKeys = self._core._crypto.generatePubKey()
        newPub = self._core._utils.bytesToStr(newKeys[0])
        newPriv = self._core._utils.bytesToStr(newKeys[1])

        command = (self.publicKey, newPub, newPriv, time, expire + time)

        c.execute("INSERT INTO myForwardKeys VALUES(?, ?, ?, ?, ?);", command)

        conn.commit()
        conn.close()
        return newPub

    def getGeneratedForwardKeys(self, genNew=True):
        # Fetch the keys we generated for the peer, that are still around
        conn = sqlite3.connect(self._core.forwardKeysFile, timeout=10)
        c = conn.cursor()
        pubkey = self.publicKey
        pubkey = self._core._utils.bytesToStr(pubkey)
        command = (pubkey,)
        keyList = [] # list of tuples containing pub, private for peer

        for result in c.execute("SELECT * FROM myForwardKeys WHERE peer = ?", command):
            keyList.append((result[1], result[2]))

        if len(keyList) == 0:
            if genNew:
                self.generateForwardKey()
                keyList = self.getGeneratedForwardKeys()
        return list(keyList)

    def addForwardKey(self, newKey, expire=DEFAULT_KEY_EXPIRE):
        if not self._core._utils.validatePubKey(newKey):
            # Do not add if something went wrong with the key
            raise onionrexceptions.InvalidPubkey(newKey)

        conn = sqlite3.connect(self._core.peerDB, timeout=10)
        c = conn.cursor()

        # Get the time we're inserting the key at
        timeInsert = self._core._utils.getEpoch()

        # Look at our current keys for duplicate key data or time
        for entry in self._getForwardKeys():
            if entry[0] == newKey:
                return False
            if entry[1] == timeInsert:
                timeInsert += 1
                time.sleep(1) # Sleep if our time is the same in order to prevent duplicate time records

        # Add a forward secrecy key for the peer
        # Prepare the insert
        command = (self.publicKey, newKey, timeInsert, timeInsert + expire)

        c.execute("INSERT INTO forwardKeys VALUES(?, ?, ?, ?);", command)

        conn.commit()
        conn.close()
        return True
    
    @classmethod
    def list_friends(cls, coreInst):
        friendList = []
        for x in coreInst.listPeers(trust=1):
            friendList.append(cls(coreInst, x))
        return list(friendList)