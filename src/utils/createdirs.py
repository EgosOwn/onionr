'''
    Onionr - Private P2P Communication

    Create required Onionr directories
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
import os
from . import identifyhome
from onionrsetup import dbcreator
import filepaths
home = identifyhome.identify_home()

def create_dirs():
    """Creates onionr data-related directories in order of the hardcoded list below,
    then trigger creation of DBs"""
    gen_dirs = [home, filepaths.block_data_location, filepaths.contacts_location, filepaths.export_location]
    for path in gen_dirs:
        if not os.path.exists(path):
            os.mkdir(path)

    for db in dbcreator.create_funcs:
        try:
            db()
        except FileExistsError:
            pass