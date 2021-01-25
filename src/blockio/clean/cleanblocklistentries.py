"""Onionr - Private P2P Communication.

Delete block type lists that are empty
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from safedb import SafeDB
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


def clean_block_list_entries(db: 'SafeDB'):
    key = db.db_conn.firstkey()
    delete_keys = []
    while key:
        if key.startswith(b'bl-'):
            if not db.get(key):
                delete_keys.append(key)
        key = db.db_conn.nextkey(key)
    for key in delete_keys:
        del db.db_conn[key]
