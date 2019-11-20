'''
    Onionr - Private P2P Communication

    This file handles the command for exporting blocks to disk
'''
'''
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
'''
import sys, os
import logger, onionrstorage
from utils import createdirs
from onionrutils import stringvalidators
import filepaths
def doExport(bHash):
    createdirs.create_dirs()
    data = onionrstorage.getData(bHash)
    with open('%s/%s.dat' % (filepaths.export_location, bHash), 'wb') as exportFile:
        exportFile.write(data)
        logger.info('Block exported as file', terminal=True)

def export_block():
    exportDir = filepaths.export_location
    try:
        if not stringvalidators.validate_hash(sys.argv[2]): raise ValueError
    except (IndexError, ValueError):
        logger.error('No valid block hash specified.', terminal=True)
        sys.exit(1)
    else:
        bHash = sys.argv[2]
        doExport(bHash)

export_block.onionr_help = "<block hash>: Export an Onionr block to a file. Export directory is in the Onionr data directory under block-export/"
