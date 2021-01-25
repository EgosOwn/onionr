"""Onionr - Private P2P Communication.

clean expired blocks
"""
from typing import TYPE_CHECKING

from kasten import Kasten
from onionrblocks.generators.anonvdf import AnonVDFGenerator
from onionrblocks.exceptions import BlockExpired

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


def clean_expired_blocks(db: 'SafeDB'):
    key = db.db_conn.firstkey()
    delete_list = set()
    # Scan all database keys and check kasten objs if they are a hash
    while key:
        try:
            if key.startswith(b'bl-') or key.startswith(b'enc'):
                key = db.db_conn.nextkey(key)
                continue
            Kasten(key, db.get(key), AnonVDFGenerator)
        except BlockExpired:
            block_type = Kasten(
                key, db.get(key),
                None, auto_check_generator=False).get_data_type()
            db.db_conn[f'bl-{block_type}'] = \
                db.db_conn[f'bl-{block_type}'].replace(key, b'')
            delete_list.add(key)
        key = db.db_conn.nextkey(key)
    for key in delete_list:
        del db.db_conn[key]
