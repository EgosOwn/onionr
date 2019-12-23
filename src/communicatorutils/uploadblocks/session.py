"""Onionr - Private P2P Communication.

Virtual upload "sessions" for blocks
"""
from typing import Union, Dict

from onionrtypes import UserID
from onionrutils import stringvalidators
from onionrutils import bytesconverter
from onionrutils import epoch
from utils import reconstructhash
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


class UploadSession:
    """Manage statistics for an Onionr block upload session.

    accept a block hash (incl. unpadded) as an argument
    """

    def __init__(self, block_hash: Union[str, bytes]):
        block_hash = bytesconverter.bytes_to_str(block_hash)
        block_hash = reconstructhash.reconstruct_hash(block_hash)
        if not stringvalidators.validate_hash(block_hash):
            raise ValueError

        self.start_time = epoch.get_epoch()
        self.block_hash = reconstructhash.deconstruct_hash(block_hash)
        self.total_fail_count: int = 0
        self.total_success_count: int = 0
        self.peer_fails: Dict[UserID, int] = {}
        self.peer_exists: Dict[UserID, bool] = {}

    def fail_peer(self, peer):
        try:
            self.peer_fails[peer] += 1
        except KeyError:
            self.peer_fails[peer] = 0

    def fail(self):
        self.total_fail_count += 1

    def success(self):
        self.total_success_count += 1
