'''
    Onionr - Private P2P Communication

    get or set information about a user id
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
import sqlite3
from .. import dbfiles
from etc import onionrvalues

def get_user_info(peer, info):
    '''
        Get info about a peer from their database entry

        id text             0
        name text,          1
        adders text,        2
        dateSeen not null,  3
        trust int           4
        hashID text         5
    '''
    conn = sqlite3.connect(dbfiles.user_id_info_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    command = (peer,)
    infoNumbers = {'id': 0, 'name': 1, 'adders': 2, 'dateSeen': 3, 'trust': 4, 'hashID': 5}
    info = infoNumbers[info]
    iterCount = 0
    retVal = ''

    for row in c.execute('SELECT * FROM peers WHERE id=?;', command):
        for i in row:
            if iterCount == info:
                retVal = i
                break
            else:
                iterCount += 1

    conn.close()

    return retVal

def set_peer_info(peer, key, data):
    '''
        Update a peer for a key
    '''

    conn = sqlite3.connect(dbfiles.user_id_info_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    command = (data, peer)

    if key not in ('id', 'name', 'pubkey', 'forwardKey', 'dateSeen', 'trust'):
        raise ValueError("Got invalid database key when setting peer info")

    c.execute('UPDATE peers SET ' + key + ' = ? WHERE id=?', command)
    conn.commit()
    conn.close()

set_user_info = set_peer_info