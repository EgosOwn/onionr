'''
    Onionr - Private P2P Communication

    Write and read the daemon queue, which is how messages are passed into the onionr daemon in a more
    direct way than the http api
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
from onionrplugins import onionrevents as events
from onionrutils import localcommand, epoch
from .. import dbfiles
from onionrsetup import dbcreator
from etc import onionrvalues

def daemon_queue()->str:
    '''
        Gives commands to the communication proccess/daemon by reading an sqlite3 database

        This function intended to be used by the client. Queue to exchange data between "client" and server.
    '''

    retData = False
    if not os.path.exists(dbfiles.daemon_queue_db):
        dbcreator.createDaemonDB()
    else:
        conn = sqlite3.connect(dbfiles.daemon_queue_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
        c = conn.cursor()
        try:
            for row in c.execute('SELECT command, data, date, min(ID), responseID FROM commands group by id'):
                retData = row
                break
        except sqlite3.OperationalError:
            dbcreator.createDaemonDB()
        else:
            if retData != False:
                c.execute('DELETE FROM commands WHERE id=?;', (retData[3],))
        conn.commit()
        conn.close()

    return retData

def daemon_queue_add(command: str, data='', responseID: str =''):
    '''
        Add a command to the daemon queue, used by the communication daemon (communicator.py)
    '''

    retData = True

    date = epoch.get_epoch()
    conn = sqlite3.connect(dbfiles.daemon_queue_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()
    t = (command, data, date, responseID)
    try:
        c.execute('INSERT INTO commands (command, data, date, responseID) VALUES(?, ?, ?, ?)', t)
        conn.commit()
    except sqlite3.OperationalError:
        retData = False
        daemon_queue()
    conn.close()
    return retData

def daemon_queue_get_response(responseID=''):
    '''
        Get a response sent by communicator to the API, by requesting to the API
    '''
    if len(responseID) == 0: raise ValueError('ResponseID should not be empty')
    resp = localcommand.local_command(dbfiles.daemon_queue_db, 'queueResponse/' + responseID)
    return resp

def clear_daemon_queue():
    '''
        Clear the daemon queue (somewhat dangerous)
    '''
    conn = sqlite3.connect(dbfiles.daemon_queue_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    c.execute('DELETE FROM commands;')
    conn.commit()

    conn.close()
