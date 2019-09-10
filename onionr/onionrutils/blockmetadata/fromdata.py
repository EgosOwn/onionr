'''
    Onionr - Private P2P Communication

    Return a useful tuple of (metadata (header), meta, and data) by accepting raw block data
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

import json

from onionrutils import bytesconverter
def get_block_metadata_from_data(block_data):
    '''
        accepts block contents as string, returns a tuple of 
        metadata, meta (meta being internal metadata, which will be 
        returned as an encrypted base64 string if it is encrypted, dict if not).
    '''
    meta = {}
    metadata = {}
    data = block_data
    try:
        block_data = block_data.encode()
    except AttributeError:
        pass

    try:
        metadata = json.loads(bytesconverter.bytes_to_str(block_data[:block_data.find(b'\n')]))
    except json.decoder.JSONDecodeError:
        pass
    else:
        data = block_data[block_data.find(b'\n'):]

        meta = metadata['meta']
    return (metadata, meta, data)
