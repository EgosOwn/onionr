'''
    Onionr - Private P2P Communication

    Public endpoints to do various block sync actions and announcement
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
from . import announce, upload, getblocks

announce = announce.handle_announce # endpoint handler for accepting peer announcements
upload = upload.accept_upload # endpoint handler for accepting public uploads
public_block_list = getblocks.get_public_block_list # endpoint handler for getting block lists
public_get_block_data = getblocks.get_block_data # endpoint handler for responding to peers requests for block data