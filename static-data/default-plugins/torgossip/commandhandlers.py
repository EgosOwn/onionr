"""Onionr - Private P2P Communication.

Handle commands for the torgossip server
"""
from onionrblocks import generators
from onionrblocks.generators import anonvdf
import blockio

import onionrblocks
from kasten import Kasten
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
def put_block(safe_db, block):
    block_hash = block[:64]
    data = block[64:]
    try:
        blockio.store_block(
            Kasten(block_hash, data, onionrblocks.generators.AnonVDFGenerator),
            safe_db)
    except ValueError:
        print("Block was seen before")
        pass
    except Exception as e:
        print("Unknown error" + repr(e))
        return b"0"
    return b"1"



def get_block(safe_db, block_hash) -> bytes:
    # 4
    try:
        return safe_db.get(block_hash)
    except KeyError:
        return b"0"


def list_blocks_by_type(safe_db, block_type) -> bytes:
    # 3
    block_type = block_type.decode('utf-8')
    print('ty', block_type)
    try:
        return safe_db.get('bl-' + block_type)
    except KeyError:
        return b"0"


def handle_check_block(safe_db, block_hash):
    # 2
    if block_hash in blockio.list_all_blocks(safe_db):
        return int(1).to_bytes(1, 'little')
    else:
        return int(2).to_bytes(1, 'little')
