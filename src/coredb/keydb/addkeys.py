"""Onionr - Private P2P Communication.

add user keys or transport addresses
"""
import sqlite3
from onionrutils import stringvalidators
from . import listkeys
from utils import gettransports
from .. import dbfiles
import onionrcrypto
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


def add_peer(peerID, name=''):
    """Add a public key to the key database (misleading function name)."""
    if peerID in listkeys.list_peers() or peerID == onionrcrypto.pub_key:
        raise ValueError("specified id is already known")

    # This function simply adds a peer to the DB
    if not stringvalidators.validate_pub_key(peerID):
        return False

    conn = sqlite3.connect(dbfiles.user_id_info_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    hashID = ""
    c = conn.cursor()
    t = (peerID, name, 'unknown', hashID, 0)

    for i in c.execute("SELECT * FROM peers WHERE id = ?;", (peerID,)):
        try:
            if i[0] == peerID:
                conn.close()
                return False
        except ValueError:
            pass
        except IndexError:
            pass
    c.execute('INSERT INTO peers (id, name, dateSeen, hashID, trust) VALUES(?, ?, ?, ?, ?);', t)
    conn.commit()
    conn.close()

    return True


def add_address(address):
    """Add an address to the address database (only tor currently)"""

    if type(address) is None or len(address) == 0:
        return False
    if stringvalidators.validate_transport(address):
        if address in gettransports.get():
            return False
        conn = sqlite3.connect(dbfiles.address_info_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
        c = conn.cursor()
        # check if address is in database
        # this is safe to do because the address is validated above, but we strip some chars here too just in case
        address = address.replace('\'', '').replace(';', '').replace('"', '').replace('\\', '')
        for i in c.execute("SELECT * FROM adders WHERE address = ?;", (address,)):
            try:
                if i[0] == address:
                    conn.close()
                    return False
            except ValueError:
                pass
            except IndexError:
                pass

        t = (address, 1)
        c.execute('INSERT INTO adders (address, type) VALUES(?, ?);', t)
        conn.commit()
        conn.close()

        return True
    else:
        return False
