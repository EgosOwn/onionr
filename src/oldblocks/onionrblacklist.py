"""Onionr - Private P2P Communication.

Handle maintenance of a blacklist database, for blocks and peers
"""
import sqlite3
import os

from onionrplugins.onionrevents import event
import onionrcrypto
from onionrutils import epoch, bytesconverter
from coredb import dbfiles
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


class OnionrBlackList:
    def __init__(self):
        self.blacklistDB = dbfiles.blacklist_db

        if not os.path.exists(dbfiles.blacklist_db):
            self.generateDB()
        return

    def inBlacklist(self, data):
        hashed = bytesconverter.bytes_to_str(
            onionrcrypto.hashers.sha3_hash(data))
        retData = False

        if not hashed.isalnum():
            raise Exception("Hashed data is not alpha numeric")
        if len(hashed) > 64:
            raise Exception("Hashed data is too large")

        for i in self._dbExecute(
                "SELECT * FROM blacklist WHERE hash = ?", (hashed,)):
            # this only executes if an entry is present by that hash
            retData = True
            break

        return retData

    def _dbExecute(self, toExec, params=()):
        conn = sqlite3.connect(self.blacklistDB, timeout=DATABASE_LOCK_TIMEOUT)
        c = conn.cursor()
        retData = c.execute(toExec, params)
        conn.commit()
        return retData

    def deleteBeforeDate(self, date):
        # TODO, delete blacklist entries before date
        return

    def deleteExpired(self, dataType=0):
        """Delete expired entries"""
        deleteList = []
        curTime = epoch.get_epoch()

        try:
            int(dataType)
        except AttributeError:
            raise TypeError("dataType must be int")

        for i in self._dbExecute(
                'SELECT * FROM blacklist WHERE dataType = ?', (dataType,)):
            if i[1] == dataType:
                if (curTime - i[2]) >= i[3]:
                    deleteList.append(i[0])

        for thing in deleteList:
            self._dbExecute("DELETE FROM blacklist WHERE hash = ?", (thing,))

    def generateDB(self):
        return

    def clearDB(self):
        self._dbExecute("""DELETE FROM blacklist;""")

    def getList(self):
        data = self._dbExecute('SELECT * FROM blacklist')
        myList = []
        for i in data:
            myList.append(i[0])
        return myList

    def addToDB(self, data, dataType=0, expire=0):
        """Add to the blacklist. Intended to be block hash, block data, peers, or transport addresses
        0=block
        1=peer
        2=pubkey
        """

        # we hash the data so we can remove data entirely from our node's disk
        hashed = bytesconverter.bytes_to_str(onionrcrypto.hashers.sha3_hash(data))

        event('blacklist_add', data={'data': data, 'hash': hashed})

        if len(hashed) > 64:
            raise Exception("Hashed data is too large")

        if not hashed.isalnum():
            raise Exception("Hashed data is not alpha numeric")
        try:
            int(dataType)
        except ValueError:
            raise Exception("dataType is not int")
        try:
            int(expire)
        except ValueError:
            raise Exception("expire is not int")
        if self.inBlacklist(hashed):
            return
        insert = (hashed,)
        blacklistDate = epoch.get_epoch()
        try:
            self._dbExecute("INSERT INTO blacklist (hash, dataType, blacklistDate, expire) VALUES(?, ?, ?, ?);", (str(hashed), dataType, blacklistDate, expire))
        except sqlite3.IntegrityError:
            pass
