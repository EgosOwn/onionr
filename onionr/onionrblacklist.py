'''
    Onionr - P2P Microblogging Platform & Social network.

    This file handles maintenence of a blacklist database, for blocks and peers
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
import sqlite3, os
class OnionrBlackList:
    def __init__(self, coreInst):
        self.blacklistDB = 'data/blacklist.db'
        self._core = coreInst
        
        if not os.path.exists(self.blacklistDB):
            self.generateDB()

        return
    
    def inBlacklist(self, data):
        return

    def _dbExecute(self, toExec):
        conn = sqlite3.connect(self.blacklistDB)
        c = conn.cursor()
        c.execute(toExec)
        conn.commit()
        conn.close()
    
    def deleteBeforeDate(self, date):
        # TODO, delete blacklist entries before date
        return

    def generateDB(self):
        self._dbExecute'''CREATE TABLE blacklist(
            hash text primary key not null,
            type text
            );
        ''')
        return
    
    def clearDB(self):
        self._dbExecute('''delete from blacklist;);''')

    
    def addToDB(self, data):
        hashed = self._core._crypto.sha3Hash(data)
        if not hashed.isalnum():
            raise Exception("Hashed data is not alpha numeric")
        insert = (hashed,)
        self._dbExecute('insert into blacklist (hash) VALUES(' + data + ');')
