"""Onionr - Private P2P Communication.

Get a list of expired blocks still stored
"""
import sqlite3
from onionrutils import epoch
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


def get_expired_blocks():
    """Return a list of expired blocks."""
    conn = sqlite3.connect(
        dbfiles.block_meta_db, timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()
    date = int(epoch.get_epoch())

    compiled = (date,)
    execute = 'SELECT hash FROM hashes WHERE ' + \
        'expire <= ? ORDER BY dateReceived;'

    rows = list()
    for row in c.execute(execute, compiled):
        for i in row:
            rows.append(i)
    conn.close()
    return rows
