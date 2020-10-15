"""Onionr - Private P2P Communication.

Perform block mixing
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

    try:
        if time.time() - bl.claimedTime > onionrvalues.BLOCK_POOL_MAX_AGE:
            raise ValueError
    except TypeError:
        pass
    if block_to_mix:
        upload_list.append(block_to_mix)
