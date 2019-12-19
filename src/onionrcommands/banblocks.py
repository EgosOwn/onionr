"""Onionr - Private P2P Communication.

This file contains the command for banning blocks from the node
"""
import sys
import logger
from onionrutils import stringvalidators
from onionrstorage import removeblock
from onionrstorage import deleteBlock
from onionrblocks import onionrblacklist
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


def ban_block():
    """Delete a block, permanently blacklisting it."""
    blacklist = onionrblacklist.OnionrBlackList()
    try:
        ban = sys.argv[2]
    except IndexError:
        # Get the hash if its not provided as a CLI argument
        ban = logger.readline('Enter a block hash:').strip()
    # Make sure the hash has no truncated zeroes
    ban = reconstructhash.reconstruct_hash(ban)
    if stringvalidators.validate_hash(ban):
        if not blacklist.inBlacklist(ban):
            try:
                blacklist.addToDB(ban)
                removeblock.remove_block(ban)
                deleteBlock(ban)
            except Exception as error:  # pylint: disable=W0703
                logger.error('Could not blacklist block',
                             error=error, terminal=True)
            else:
                logger.info('Block blacklisted', terminal=True)
        else:
            logger.warn('That block is already blacklisted', terminal=True)
    else:
        logger.error('Invalid block hash', terminal=True)


ban_block.onionr_help = "<block hash>: "  # type: ignore
ban_block.onionr_help += "deletes and blacklists a block"  # type: ignore
