'''
    Onionr - Private P2P Communication

    get lists for user keys or transport addresses
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
import logger
from onionrutils import epoch
from etc import onionrvalues
from .. import dbfiles
from . import userinfo

def list_pub_keys(randomOrder=True, getPow=False, trust=0):
    '''
        Return a list of public keys (misleading function name)

        randomOrder determines if the list should be in a random order
        trust sets the minimum trust to list
    '''
    conn = sqlite3.connect(dbfiles.user_id_info_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    payload = ''

    if trust not in (0, 1, 2):
        logger.error('Tried to select invalid trust.')
        return

    if randomOrder:
        payload = 'SELECT * FROM peers WHERE trust >= ? ORDER BY RANDOM();'
    else:
        payload = 'SELECT * FROM peers WHERE trust >= ?;'

    peerList = []

    for i in c.execute(payload, (trust,)):
        try:
            if len(i[0]) != 0:
                if getPow:
                    peerList.append(i[0] + '-' + i[1])
                else:
                    peerList.append(i[0])
        except TypeError:
            pass

    conn.close()

    return peerList
