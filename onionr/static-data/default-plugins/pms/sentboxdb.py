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
    def __init__(self, core):
        assert isinstance(core, core.Core)
        self.dbLocation = core.dataDir + 'sentbox.db'
        if not os.path.exists(self.dbLocation):
            self.createDB()
        self.conn = sqlite3.connect(self.dbLocation)
        self.cursor = self.conn.cursor()
        return
    
    def createDB(self):
        self.cursor.execute('''CREATE TABLE sent(
            hash id not null,
            peer text not null,
            message text not null,
            date int not null
            );
        ''')
        self.conn.commit()
        return

    def listSent(self):
        retData = []
        for entry in self.cursor.execute('SELECT * FROM sent;'):
            retData.append({'hash': entry[0], 'peer': entry[1], 'message': entry[2], 'date': entry[3]})
        return retData
    
    def addToSent(self, blockID):
        return
    
    def removeSent(self, blockID):
        return