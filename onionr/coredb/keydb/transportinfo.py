'''
    Onionr - Private P2P Communication

    get or set transport address meta information
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
def get_address_info(core_inst, address, info):
    '''
        Get info about an address from its database entry

        address text, 0
        type int, 1
        knownPeer text, 2
        speed int, 3
        success int, 4
        powValue    5
        failure int 6
        lastConnect 7
        trust       8
        introduced  9
    '''

    conn = sqlite3.connect(core_inst.addressDB, timeout=30)
    c = conn.cursor()

    command = (address,)
    infoNumbers = {'address': 0, 'type': 1, 'knownPeer': 2, 'speed': 3, 'success': 4, 'powValue': 5, 'failure': 6, 'lastConnect': 7, 'trust': 8, 'introduced': 9}
    info = infoNumbers[info]
    iterCount = 0
    retVal = ''

    for row in c.execute('SELECT * FROM adders WHERE address=?;', command):
        for i in row:
            if iterCount == info:
                retVal = i
                break
            else:
                iterCount += 1
    conn.close()

    return retVal

def set_address_info(core_inst, address, key, data):
    '''
        Update an address for a key
    '''

    conn = sqlite3.connect(core_inst.addressDB, timeout=30)
    c = conn.cursor()

    command = (data, address)

    if key not in ('address', 'type', 'knownPeer', 'speed', 'success', 'failure', 'powValue', 'lastConnect', 'lastConnectAttempt', 'trust', 'introduced'):
        raise Exception("Got invalid database key when setting address info")
    else:
        c.execute('UPDATE adders SET ' + key + ' = ? WHERE address=?', command)
        conn.commit()
    conn.close()