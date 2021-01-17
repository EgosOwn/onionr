"""Onionr - Private P2P Communication.

Store blocks and cache meta info such as block type
"""
from typing import TYPE_CHECKING, Union, NewType

from safedb import DBProtectionOpeningModeError

if TYPE_CHECKING:
    from kasten import Kasten
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

RawBlock = NewType('RawBlock', bytes)


def store_block(block: Kasten, safe_db: SafeDB):
    
    safe_db.put(block.id, block.get_packed())

