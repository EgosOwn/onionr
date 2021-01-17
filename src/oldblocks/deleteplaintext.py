"""Onionr - P2P Anonymous Storage Network.

Delete but do not blacklist plaintext blocks
"""
from coredb import blockmetadb
from onionrstorage.removeblock import remove_block
import onionrstorage
from .onionrblockapi import Block
import onionrexceptions
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


def delete_plaintext_no_blacklist():
    """Delete, but do not blacklist, plaintext blocks."""

    block_list = blockmetadb.get_block_list()

    for block in block_list:
        block = Block(hash=block, decrypt=False)
        if not block.isEncrypted:
            remove_block(block.hash)  # delete metadata entry
            onionrstorage.deleteBlock(block.hash)  # delete block data
