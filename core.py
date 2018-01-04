'''
    Onionr - P2P Microblogging Platform & Social network
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
import sqlite3, os, time, math
class Core:
    def __init__(self):
        self.queueDB = 'data/queue.db'
        #self.daemonQueue() # Call to create the DB if it doesn't exist
        return

    def daemonQueue(self):
        # This function intended to be used by the client
        # Queue to exchange data between "client" and server.
        retData = False
        if not os.path.exists(self.queueDB):
            conn = sqlite3.connect(self.queueDB)
            c = conn.cursor()
            # Create table
            c.execute('''CREATE TABLE commands
                        (id integer primary key autoincrement, command text, data text, date text)''')
            conn.commit()
            print('created table')
        else:
            conn = sqlite3.connect(self.queueDB)
            c = conn.cursor()
            for row in c.execute('SELECT command, data, date, min(ID) FROM commands group by id'):
                retData = row
                print(retData)
                break
            if retData != False:
                print('3', retData[3])
                c.execute('delete from commands where id = ?', (retData[3],))
        conn.commit()
        conn.close()

        return retData

    def daemonQueueAdd(self, command, data=''):
        # Intended to be used by the web server
        date = math.floor(time.time())
        conn = sqlite3.connect(self.queueDB)
        c = conn.cursor()
        t = (command, data, date)
        c.execute('INSERT into commands (command, data, date) values (?, ?, ?)', t)
        conn.commit()
        conn.close()
        return