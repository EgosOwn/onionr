"""Onionr - Private P2P Communication.

Command to make new network-wide MOTD message. Only network admin can do this
The key is set in onionrvalues
"""
import onionrblocks
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


def motd_creator():
    """Create a new MOTD message for the Onionr network."""
    motd = ''
    new = ''
    print('Enter a new MOTD, quit on a new line:')
    while new != 'quit':
        new = input()  # nosec B323
        if new != 'quit':
            motd += new
    bl = onionrblocks.insert(motd, header='motd', sign=True)
    print(f"inserted in {bl}")


motd_creator.onionr_help = "Create a new MOTD for the network"  # type: ignore
