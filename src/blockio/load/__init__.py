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
    blocks = safe_db.get(f'bl-{block_type}')
    return zip(*[iter(blocks)]*64)
