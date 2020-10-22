"""Onionr - Private P2P Communication.

Upload pool
"""
from typing import List
from secrets import SystemRandom

import onionrutils
import onionrtypes
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


class PoolFullException(Exception):
    """For when the UploadPool is full.

    Raise when a new hash is attempted to be added
    """


class PoolNotReady(Exception):
    """Raise when UploadPool pool access is attempted without it being full."""


class AlreadyInPool(Exception):
    """Raise when a hash already in pool is attempted to be added again."""


class UploadPool:
    """Upload pool for mixing blocks together and delaying uploads."""

    def __init__(self, pool_size: int):
        """Create a new pool with a specified max size.

        Uses private var and getter to avoid direct adding
        """
        self._pool: List[onionrtypes.BlockHash] = []
        self._pool_size = pool_size
        self.birthday = onionrutils.epoch.get_epoch()

    def add_to_pool(self, item: List[onionrtypes.BlockHash]):
        """Add a new hash to the pool. Raise PoolFullException if full."""
        if len(self._pool) >= self._pool_size:
            raise PoolFullException
        if not onionrutils.stringvalidators.validate_hash(item):
            raise ValueError
        self._pool.append(item)

    def get_pool(self) -> List[onionrtypes.BlockHash]:
        """Get the hash pool in secure random order."""
        if len(self._pool) != self._pool_size:
            raise PoolNotReady

        final_pool: List[onionrtypes.BlockHash] = list(self._pool)
        SystemRandom().shuffle(final_pool)

        self._pool.clear()
        self.birthday = onionrutils.epoch.get_epoch()
        return final_pool
