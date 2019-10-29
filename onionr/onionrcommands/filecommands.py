"""
    Onionr - Private P2P Communication

    This file handles the commands for adding and getting files from the Onionr network
"""
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

import base64, sys, os
import logger
from onionrblocks.onionrblockapi import Block
import onionrexceptions
from onionrutils import stringvalidators
from etc import onionrvalues
from onionrblocks import insert
_ORIG_DIR = onionrvalues.ORIG_RUN_DIR_ENV_VAR

def _get_dir(path: str)->str: 
    if not os.getenv(_ORIG_DIR) is None: return os.getenv(_ORIG_DIR) + '/' + path
    else: return path

def add_html(singleBlock=True, blockType='html'):
    add_file(singleBlock, blockType)

add_html.onionr_help = "Adds an HTML file into Onionr. Does not currently include dependant resources"

def add_file(singleBlock=False, blockType='bin'):
    """
        Adds a file to the onionr network
    """

    if len(sys.argv) >= 3:
        filename = sys.argv[2]
        contents = None
        if not os.path.exists(_get_dir(filename)):
            logger.error('That file does not exist. Improper path (specify full path)?', terminal=True)
            return
        logger.info('Adding file... this might take a long time.', terminal=True)
        try:
            with open(_get_dir(filename), 'rb') as singleFile:
                blockhash = insert(singleFile.read(), header=blockType)
            if len(blockhash) > 0:
                logger.info('File %s saved in block %s' % (filename, blockhash), terminal=True)
        except Exception as e:
            logger.error('Failed to save file in block ' + str(e), timestamp = False, terminal=True)
    else:
        logger.error('%s add-file <filename>' % sys.argv[0], timestamp = False, terminal=True)

add_file.onionr_help = "<file path> Add a file into the Onionr network"

def get_file():
    """
        Get a file from onionr blocks
    """
    try:
        fileName = _get_dir(sys.argv[2])
        bHash = sys.argv[3]
    except IndexError:
        logger.error("Syntax %s %s" % (sys.argv[0], '/path/to/filename <blockhash>'), terminal=True)
    else:
        logger.info(fileName, terminal=True)

        contents = None
        if os.path.exists(fileName):
            logger.error("File already exists", terminal=True)
            return
        if not stringvalidators.validate_hash(bHash):
            logger.error('Block hash is invalid', terminal=True)
            return

        try:
            with open(fileName, 'wb') as myFile:
                myFile.write(Block(bHash).bcontent)
        except onionrexceptions.NoDataAvailable:
            logger.error('That block is not available. Trying again later may work.', terminal=True)

get_file.onionr_help = "<file path> <block hash>: Download a file from the onionr network."
