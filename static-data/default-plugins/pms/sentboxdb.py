"""
    Onionr - Private P2P Communication

    This file handles the sentbox for the mail plugin
"""
import sqlite3
import os
from onionrutils import epoch
from utils import identifyhome, reconstructhash
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


class SentBox:
    def __init__(self):
        self.dbLocation = identifyhome.identify_home() + '/sentbox.db'
        if not os.path.exists(self.dbLocation):
            self.createDB()
        return

    def connect(self):
        self.conn = sqlite3.connect(self.dbLocation, timeout=30)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def createDB(self):
        conn = sqlite3.connect(self.dbLocation)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE sent(
            hash id not null,
            peer text not null,
            message text not null,
            subject text not null,
            date int not null
            );
        """)
        conn.commit()
        conn.close()
        return

    def listSent(self):
        self.connect()
        retData = []
        for entry in self.cursor.execute('SELECT * FROM sent;'):
            retData.append({'hash': entry[0], 'peer': entry[1], 'message': entry[2], 'subject': entry[3], 'date': entry[4]})
        self.close()
        return retData

    def addToSent(self, blockID, peer, message, subject=''):
        blockID = reconstructhash.deconstruct_hash(blockID)
        self.connect()
        args = (blockID, peer, message, subject, epoch.get_epoch())
        self.cursor.execute('INSERT INTO sent VALUES(?, ?, ?, ?, ?)', args)
        self.conn.commit()
        self.close()
        return

    def removeSent(self, blockID):
        blockID = reconstructhash.deconstruct_hash(blockID)
        self.connect()
        args = (blockID,)
        self.cursor.execute('DELETE FROM sent where hash=?', args)
        self.conn.commit()
        self.close()
        return
