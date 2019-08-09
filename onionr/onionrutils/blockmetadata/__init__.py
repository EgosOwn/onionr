'''
    Onionr - Private P2P Communication

    Module to work with block metadata
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

from . import hasblock, fromdata, process
has_block = hasblock.has_block
process_block_metadata = process.process_block_metadata
get_block_metadata_from_data = fromdata.get_block_metadata_from_data
