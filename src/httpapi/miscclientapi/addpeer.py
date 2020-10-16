"""Onionr - Private P2P Communication.

add a transport address to the db
"""
from onionrutils.stringvalidators import validate_transport
from coredb.keydb.addkeys import add_address
from coredb.keydb.listkeys import list_adders
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


def add_peer(peer):

    if peer in list_adders():
        return "already added"
    if add_address(peer):
        return "success"
    else:
        return "failure, invalid address"
