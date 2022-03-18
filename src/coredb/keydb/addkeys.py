"""Onionr - Private P2P Communication.

add user keys or transport addresses
"""
import sqlite3
from onionrutils import stringvalidators
from . import listkeys
from .. import dbfiles
import onionrcrypto
import onionrvalues
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


def add_pub_key(peerID, name=''):
    """Add a public key to the key database (misleading function name)."""
    if peerID in listkeys.list_pub_keys() or peerID == onionrcrypto.pub_key:
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

