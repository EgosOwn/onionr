"""Onionr - Private P2P Communication.

Delay block uploads, optionally mixing them together
"""
import time
from typing import List

import onionrtypes
from onionrblocks import onionrblockapi

from .pool import UploadPool
from .pool import PoolFullException

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
upload_pool = UploadPool(4)


def block_mixer(upload_list: List[onionrtypes.BlockHash],
                block_to_mix: onionrtypes.BlockHash):
    """Delay and mix block inserts.

    Take a block list and a received/created block and add it
    to the said block list
    """
    bl = onionrblockapi.Block(block_to_mix)
    if time.time() - bl.claimedTime > onionrvalues.BLOCK_POOL_MAX_AGE:
        raise ValueError

    try:
        # add the new block to pool
        upload_pool.add_to_pool(block_to_mix)
    except PoolFullException:
        # If the pool is full, move into upload queue
        upload_list.extend(upload_pool.get_pool())
        # then finally begin new pool with new block
        upload_pool.add_to_pool(block_to_mix)
