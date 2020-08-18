"""Onionr - Private P2P Communication.

get or set transport address meta information
"""
import sqlite3
from .. import dbfiles
from etc import onionrvalues
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
info_numbers = {
    'address': 0,
    'type': 1,
    'knownPeer': 2,
    'speed': 3,
    'success': 4,
    'powValue': 5,
    'failure': 6,
    'lastConnect': 7,
    'trust': 8,
    'introduced': 9}


def get_address_info(address, info):
    """Get info about an address from its database entry.

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
    """
    conn = sqlite3.connect(
        dbfiles.address_info_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    command = (address,)

    info = info_numbers[info]
    iter_count = 0
    retVal = ''

    for row in c.execute('SELECT * FROM adders WHERE address=?;', command):
        for i in row:
            if iter_count == info:
                retVal = i
                break
            else:
                iter_count += 1
    conn.close()

    return retVal


def set_address_info(address, key, data):
    """Update an address for a key."""
    conn = sqlite3.connect(
        dbfiles.address_info_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()

    command = (data, address)

    if key not in info_numbers.keys():
        raise ValueError(
            "Got invalid database key when setting address info, must be in whitelist")
    else:
        c.execute('UPDATE adders SET ' + key + ' = ? WHERE address=?', command)
        conn.commit()
    conn.close()