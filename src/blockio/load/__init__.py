"""Onionr - Private P2P Communication.

Get blocks from safedb
"""
from typing import TYPE_CHECKING, List

from kasten import Kasten

if TYPE_CHECKING:
    from kasten.types import BlockChecksumBytes
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


def load_block(block: 'BlockChecksumBytes', safe_db: 'SafeDB') -> Kasten:
    return Kasten(
        block, safe_db.get(block), generator=None, auto_check_generator=False)


def list_blocks_by_type(
        block_type: str, safe_db: 'SafeDB') -> List['BlockChecksumBytes']:
    try:
        block_type = block_type.decode('utf-8')
    except AttributeError:
        pass
    blocks = safe_db.get(f'bl-{block_type}')
    return zip(*[iter(blocks)]*64)


def list_all_blocks(safe_db: 'SafeDB'):
    # Builds and return a master list of blocks by identifying all type lists
    # and iterating them
    key = safe_db.db_conn.firstkey()
    master_list = []
    while key:
        if key.startswith(b'bl-'):
            master_list.extend(
                list(list_blocks_by_type(key.replace(b'bl-', b''), safe_db)))
        key = safe_db.db_conn.nextkey(key)
    return master_list

