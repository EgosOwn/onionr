"""Onionr - Private P2P Communication.

Update block information in the metadata database by a field name
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


def update_block_info(hash, key, data):
    """set info associated with a block

        hash         - the hash of a block
        dateReceived - the date the block was recieved, not necessarily when it was created
        decrypted    - if we can successfully decrypt the block
        dataType     - data type of the block
        dataFound    - if the data has been found for the block
        dataSaved    - if the data has been saved for the block
        sig          - defunct
        author       - defunct
        dateClaimed  - timestamp claimed inside the block, only as trustworthy as the block author is
        expire       - expire date for a block
    """
    if key not in ('dateReceived', 'decrypted', 'dataType', 'dataFound',
                   'dataSaved', 'sig', 'author', 'dateClaimed', 'expire'):
        raise ValueError('Key must be in the allowed list')

    conn = sqlite3.connect(dbfiles.block_meta_db,
                           timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()
    args = (data, hash)
    # Unfortunately, not really possible to prepare this statement
    c.execute("UPDATE hashes SET " + key + " = ? where hash = ?;", args)
    conn.commit()
    conn.close()

    return True
