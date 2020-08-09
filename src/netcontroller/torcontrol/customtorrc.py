"""Onionr - Private P2P Communication.

Load or set custom torrc
"""
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

CUSTOM_TORRC_FILE = identifyhome.identify_home() + '/torrc-custom'


def set_custom_torrc(torrc_data: str):
    """write torrc_data to custom torrc file stored in home dir.
    if set it will be used in addition to onionr's generated settings
    """
    torrc_comment = f'\n# BEGIN CUSTOM TORRC FROM {CUSTOM_TORRC_FILE}\n'
    torrc_data = torrc_comment + torrc_data
    with open(CUSTOM_TORRC_FILE, 'w') as torrc:
        torrc.write(torrc_data)


def get_custom_torrc() -> str:
    """read torrc_data from custom torrc file stored in home dir.
    if set it will be used in addition to onionr's generated settings
    """
    torrc = ''
    try:
        with open(CUSTOM_TORRC_FILE, 'r') as torrc:
            torrc = torrc.read()
    except FileNotFoundError:
        pass
    return '\n' + torrc
