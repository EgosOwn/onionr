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
import sys
import logger, onionrstorage
def doExport(o_inst, bHash):
    exportDir = o_inst.dataDir + 'block-export/'
    if not os.path.exists(exportDir):
        if os.path.exists(o_inst.dataDir):
            os.mkdir(exportDir)
        else:
            logger.error('Onionr Not initialized')
    data = onionrstorage.getData(o_inst.onionrCore, bHash)
    with open('%s/%s.dat' % (exportDir, bHash), 'wb') as exportFile:
        exportFile.write(data)

def export_block(o_inst):
    exportDir = o_inst.dataDir + 'block-export/'
    try:
        assert o_inst.onionrUtils.validateHash(sys.argv[2])
    except (IndexError, AssertionError):
        logger.error('No valid block hash specified.')
        sys.exit(1)
    else:
        bHash = sys.argv[2]
        o_inst.doExport(bHash)