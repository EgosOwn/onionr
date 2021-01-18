"""
Onionr - Private P2P Communication.

Preset Onionr usernames
"""
import locale
locale.setlocale(locale.LC_ALL, '')

from utils import identifyhome
from onionrusers import contactmanager
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

plugin_name = 'usernames'


def on_onboard(api, data=None):
    username_file = identifyhome.identify_home() + f'plugins/{plugin_name}/usernames.dat'
    with open(username_file, 'r') as usernames:
        username_and_keys = usernames.readlines()

    for entry in username_and_keys:
        username, key = entry.split(',')
        username = username.strip()
        if not username:
            continue
        key = key.strip()
        user = contactmanager.ContactManager(key, saveUser=True)
        user.set_info('name', username)



