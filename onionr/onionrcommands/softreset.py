"""
    Onionr - Private P2P Communication

    Command to soft-reset Onionr (deletes blocks)
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
import os
import shutil

from onionrutils import localcommand
from coredb import dbfiles
import filepaths
import logger
def soft_reset():
    if localcommand.local_command('/ping') == 'pong!':
        logger.warn('Cannot soft reset while Onionr is running', terminal=True)
        return
    path = filepaths.block_data_location
    shutil.rmtree(path)
    os.remove(dbfiles.block_meta_db)
    logger.info("Soft reset Onionr", terminal=True)

soft_reset.onionr_help = "Deletes Onionr blocks and their associated metadata, except for any exported block files."