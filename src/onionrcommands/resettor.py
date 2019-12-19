"""Onionr - Private P2P Communication.

Command to delete the Tor data directory if its safe to do so
"""
import os
import shutil
import logger
from onionrutils import localcommand
from utils import identifyhome
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


def __delete(directory):
    tor_dir = '%s/%s/' % (identifyhome.identify_home(), directory)
    if os.path.exists(tor_dir):
        if localcommand.local_command('/ping') == 'pong!':
            logger.warn(
                'Cannot delete Tor data while Onionr is running',
                terminal=True)
        else:
            shutil.rmtree(tor_dir)
            logger.info('Tor reset', terminal=True)


def reset_tor():
    """Delete tor data directory."""
    __delete('tordata')


reset_tor.onionr_help = "Deletes Onionr's Tor data directory. "  # type: ignore
reset_tor.onionr_help += "Only do this as a last resort if "  # type: ignore
reset_tor.onionr_help += "you have serious Tor issues."  # type: ignore


def reset_tor_key_pair():
    """Delete Tor HS key pair for our node."""
    __delete('hs')


reset_tor_key_pair.onionr_help = "Delete's your Tor "  # type: ignore
reset_tor_key_pair.onionr_help += "node address permanently. "  # type: ignore
reset_tor_key_pair.onionr_help += "Note that through "  # type: ignore
reset_tor_key_pair.onionr_help += "fingerprinting attackers "  # type: ignore
reset_tor_key_pair.onionr_help += "may be able to know that "  # type: ignore
reset_tor_key_pair.onionr_help += "your new generated node "  # type: ignore
reset_tor_key_pair.onionr_help += "address belongs to "  # type: ignore
reset_tor_key_pair.onionr_help += "the same node "  # type: ignore
reset_tor_key_pair.onionr_help += "as the deleted one."  # type: ignore
