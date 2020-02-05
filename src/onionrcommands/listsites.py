"""Onionr - Private P2P Communication.

Dumb listing of Onionr sites
"""
from coredb.blockmetadb import get_blocks_by_type
from onionrblocks.onionrblockapi import Block
import logger
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


def print_site_list():
    """Create a new MOTD message for the Onionr network."""
    block_list = get_blocks_by_type('osite')
    if not block_list:
        logger.info('No sites saved right now', terminal=True)
    for block in block_list:
        block = Block(block)
        if block.isSigned():
            logger.info(block.signer.replace('=', ''), terminal=True)
        else:
            logger.info(block.hash, terminal=True)


print_site_list.onionr_help = "Dumbly list all Onionr sites currently saved"  # type: ignore
