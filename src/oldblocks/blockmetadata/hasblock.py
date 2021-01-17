"""Onionr - Private P2P Communication.

Return a bool if a block is in the block metadata db or not
"""
import sqlite3
from coredb import dbfiles
import onionrexceptions
from onionrutils import stringvalidators
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


def has_block(hash: str) -> bool:
    """Check for new block in the block meta db."""
    conn = sqlite3.connect(
        dbfiles.block_meta_db,
        timeout=onionrvalues.DATABASE_LOCK_TIMEOUT)
    c = conn.cursor()
    if not stringvalidators.validate_hash(hash):
        raise onionrexceptions.InvalidHexHash("Invalid hash")
    for result in c.execute("SELECT COUNT() FROM hashes WHERE hash = ?", (hash,)):
        if result[0] >= 1:
            conn.commit()
            conn.close()
            return True
        else:
            conn.commit()
            conn.close()
            return False
    return False
