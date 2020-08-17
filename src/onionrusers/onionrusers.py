"""Onionr - Private P2P Communication.

Contains abstractions for interacting with users of Onionr
"""
import sqlite3
import time

import onionrexceptions
from onionrutils import stringvalidators, bytesconverter, epoch

import unpaddedbase32
import nacl.exceptions

from coredb import keydb, dbfiles
import onionrcrypto
from onionrcrypto import getourkeypair
from etc.onionrvalues import DATABASE_LOCK_TIMEOUT
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


def deleteExpiredKeys():
    # Fetch the keys we generated for the peer, that are still around
    conn = sqlite3.connect(
        dbfiles.forward_keys_db, timeout=DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    curTime = epoch.get_epoch()
    c.execute("DELETE from myForwardKeys where expire <= ?", (curTime,))
    conn.commit()
    conn.execute("VACUUM")
    conn.close()
    return


def deleteTheirExpiredKeys(pubkey):
    conn = sqlite3.connect(
        dbfiles.user_id_info_db, timeout=DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    # Prepare the insert
    command = (pubkey, epoch.get_epoch())

    c.execute("DELETE from forwardKeys where peerKey = ? and expire <= ?", command)

    conn.commit()
    conn.close()


DEFAULT_KEY_EXPIRE = 604800


class OnionrUser:

    def __init__(self, publicKey, saveUser=False):
        """
        OnionrUser is an abstraction for "users" of the network.

        Takes a base32 encoded ed25519 public key, and a bool saveUser
        saveUser determines if we should add a user to our peer database or not.
        """
        publicKey = unpaddedbase32.repad(
            bytesconverter.str_to_bytes(publicKey)).decode()

        self.trust = 0
        self.publicKey = publicKey

        if saveUser and not publicKey == getourkeypair.get_keypair():
            try:
                keydb.addkeys.add_peer(publicKey)
            except (AssertionError, ValueError) as _:
                pass

        self.trust = keydb.userinfo.get_user_info(self.publicKey, 'trust')
        return

    def setTrust(self, newTrust):
        """Set the peers trust. 0 = not trusted, 1 = friend, 2 = ultimate"""
        keydb.userinfo.set_user_info(self.publicKey, 'trust', newTrust)

    def isFriend(self):
        if keydb.userinfo.get_user_info(self.publicKey, 'trust') == 1:
            return True
        return False

    def getName(self):
        retData = 'anonymous'
        name = keydb.userinfo.get_user_info(self.publicKey, 'name')
        try:
            if len(name) > 0:
                retData = name
        except ValueError:
            pass
        return retData

    def encrypt(self, data):
        encrypted = onionrcrypto.encryption.pub_key_encrypt(
            data, self.publicKey, encodedData=True)
        return encrypted

    def decrypt(self, data):
        decrypted = onionrcrypto.encryption.pub_key_decrypt(
            data, self.publicKey, encodedData=True)
        return decrypted

    def forwardEncrypt(self, data):
        deleteTheirExpiredKeys(self.publicKey)
        deleteExpiredKeys()
        retData = ''
        forwardKey = self._getLatestForwardKey()
        if stringvalidators.validate_pub_key(forwardKey[0]):
            retData = onionrcrypto.encryption.pub_key_encrypt(
                data, forwardKey[0], encodedData=True)
        else:
            raise onionrexceptions.InvalidPubkey(
                "No valid forward secrecy key available for this user")
        return (retData, forwardKey[0], forwardKey[1])

    def forwardDecrypt(self, encrypted):
        retData = ""
        for key in self.getGeneratedForwardKeys(False):
            try:
                retData = onionrcrypto.encryption.pub_key_decrypt(
                    encrypted, privkey=key[1], encodedData=True)
            except nacl.exceptions.CryptoError:
                retData = False
            else:
                break
        else:
            raise onionrexceptions.DecryptionError(
                "Could not decrypt forward secrecy content")
        return retData

    def _getLatestForwardKey(self):
        # Get the latest forward secrecy key for a peer
        key = ""
        conn = sqlite3.connect(
            dbfiles.user_id_info_db, timeout=DATABASE_LOCK_TIMEOUT)
        c = conn.cursor()

        # TODO: account for keys created at the same time (same epoch)
        for row in c.execute(
                "SELECT forwardKey, max(EXPIRE) FROM forwardKeys WHERE peerKey = ? ORDER BY expire DESC",  # noqa
                (self.publicKey,)):
            key = (row[0], row[1])
            break

        conn.commit()
        conn.close()

        return key

    def _getForwardKeys(self):
        conn = sqlite3.connect(
            dbfiles.user_id_info_db, timeout=DATABASE_LOCK_TIMEOUT)
        c = conn.cursor()
        keyList = []

        for row in c.execute(
                "SELECT forwardKey, date FROM forwardKeys WHERE peerKey = ? ORDER BY expire DESC",  # noqa
                (self.publicKey,)):
            keyList.append((row[0], row[1]))

        conn.commit()
        conn.close()

        return list(keyList)

    def generateForwardKey(self, expire=DEFAULT_KEY_EXPIRE):

        # Generate a forward secrecy key for the peer
        conn = sqlite3.connect(
            dbfiles.forward_keys_db, timeout=DATABASE_LOCK_TIMEOUT)
        c = conn.cursor()
        # Prepare the insert
        time = epoch.get_epoch()
        newKeys = onionrcrypto.generate()
        newPub = bytesconverter.bytes_to_str(newKeys[0])
        newPriv = bytesconverter.bytes_to_str(newKeys[1])

        command = (self.publicKey, newPub, newPriv, time, expire + time)

        c.execute("INSERT INTO myForwardKeys VALUES(?, ?, ?, ?, ?);", command)

        conn.commit()
        conn.close()
        return newPub

    def getGeneratedForwardKeys(self, genNew=True):
        # Fetch the keys we generated for the peer, that are still around
        conn = sqlite3.connect(
            dbfiles.forward_keys_db, timeout=DATABASE_LOCK_TIMEOUT)
        c = conn.cursor()
        pubkey = self.publicKey
        pubkey = bytesconverter.bytes_to_str(pubkey)
        command = (pubkey,)
        keyList = []  # list of tuples containing pub, private for peer

        for result in c.execute(
                "SELECT * FROM myForwardKeys WHERE peer = ?", command):
            keyList.append((result[1], result[2]))

        if len(keyList) == 0:
            if genNew:
                self.generateForwardKey()
                keyList = self.getGeneratedForwardKeys()
        return list(keyList)

    def addForwardKey(self, newKey, expire=DEFAULT_KEY_EXPIRE):
        newKey = bytesconverter.bytes_to_str(
            unpaddedbase32.repad(bytesconverter.str_to_bytes(newKey)))
        if not stringvalidators.validate_pub_key(newKey):
            # Do not add if something went wrong with the key
            raise onionrexceptions.InvalidPubkey(newKey)

        conn = sqlite3.connect(
            dbfiles.user_id_info_db, timeout=DATABASE_LOCK_TIMEOUT)
        c = conn.cursor()

        # Get the time we're inserting the key at
        timeInsert = epoch.get_epoch()

        # Look at our current keys for duplicate key data or time
        for entry in self._getForwardKeys():
            if entry[0] == newKey:
                return False
            if entry[1] == timeInsert:
                timeInsert += 1
                # Sleep if our time is the same to prevent dupe time records
                time.sleep(1)

        # Add a forward secrecy key for the peer
        # Prepare the insert
        command = (self.publicKey, newKey, timeInsert, timeInsert + expire)

        c.execute("INSERT INTO forwardKeys VALUES(?, ?, ?, ?);", command)

        conn.commit()
        conn.close()
        return True

    @classmethod
    def list_friends(cls):
        friendList = []
        for x in keydb.listkeys.list_peers(trust=1):
            friendList.append(cls(x))
        return list(friendList)
