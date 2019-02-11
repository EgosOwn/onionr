'''
    Onionr - P2P Microblogging Platform & Social network

    This file handles the sentbox for the mail plugin
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
import core
class SentBox:
    def __init__(self, mycore):
        assert isinstance(mycore, core.Core)
        self.dbLocation = mycore.dataDir + 'sentbox.db'
        if not os.path.exists(self.dbLocation):
            self.createDB()
        self.conn = sqlite3.connect(self.dbLocation)
        self.cursor = self.conn.cursor()
        self.core = mycore
        return

    def createDB(self):
        conn = sqlite3.connect(self.dbLocation)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE sent(
            hash id not null,
            peer text not null,
            message text not null,
            subject text not null,
            date int not null
            );
        ''')
        conn.commit()
        return

    def listSent(self):
        retData = []
        for entry in self.cursor.execute('SELECT * FROM sent;'):
            retData.append({'hash': entry[0], 'peer': entry[1], 'message': entry[2], 'subject': entry[3], 'date': entry[4]})
        return retData

    def addToSent(self, blockID, peer, message, subject=''):
        args = (blockID, peer, message, subject, self.core._utils.getEpoch())
        self.cursor.execute('INSERT INTO sent VALUES(?, ?, ?, ?, ?)', args)
        self.conn.commit()
        return

    def removeSent(self, blockID):
        args = (blockID,)
        self.cursor.execute('DELETE FROM sent where hash=?', args)
        self.conn.commit()
        return
