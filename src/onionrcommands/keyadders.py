"""Onionr - Private P2P Communication.

add keys (transport and pubkey)
"""
import sys
import logger
from coredb import keydb
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


def add_address():
    """Command to add a peer address from either an arg or stdin."""
    try:
        newAddress = sys.argv[2]
        newAddress = newAddress.replace('http:', '').replace('/', '')
    except IndexError:
        pass
    else:
        logger.info("Adding address: " + logger.colors.underline + newAddress,
                    terminal=True)
        if keydb.addkeys.add_address(newAddress):
            logger.info("Successfully added address.", terminal=True)
        else:
            logger.warn("Unable to add address.", terminal=True)


add_address.onionr_help = "Adds a node transport address"  # type: ignore
