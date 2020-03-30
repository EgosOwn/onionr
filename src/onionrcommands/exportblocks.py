"""Onionr - Private P2P Communication.

This file handles the command for exporting blocks to disk
"""
import sys

import logger
import onionrstorage
from utils import createdirs
from onionrutils import stringvalidators
from etc.onionrvalues import BLOCK_EXPORT_FILE_EXT
import filepaths

import os
from coredb import blockmetadb
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


def _do_export(b_hash):
    createdirs.create_dirs()
    data = onionrstorage.getData(b_hash)
    with open('%s/%s%s' % (filepaths.export_location,
                             b_hash, BLOCK_EXPORT_FILE_EXT), 'wb') as export:
        export.write(data)
        logger.info('Block exported as file', terminal=True)


def export_block(*args):
    """Export block based on hash from stdin or argv."""
    if args:
        b_hash = args[0]
    else:
        try:
            if not stringvalidators.validate_hash(sys.argv[2]):
                raise ValueError
        except (IndexError, ValueError):
            logger.error('No valid block hash specified.', terminal=True)
            sys.exit(1)
        else:
            b_hash = sys.argv[2]
    _do_export(b_hash)


export_block.onionr_help = "<block hash>: Export block to "  # type: ignore
export_block.onionr_help += "a file. Export directory is in "  # type: ignore
export_block.onionr_help += "Onionr home under block-export"  # type: ignore
