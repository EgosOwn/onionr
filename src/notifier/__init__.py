"""Onionr - Private P2P Communication.

Desktop notification wrapper
"""
try:
    import simplenotifications as simplenotify
except ImportError:
    notifications_enabled = False
else:
    notifications_enabled = True

import config

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

if not config.get('general.show_notifications', True):
    notifications_enabled = False


def notify(title: str = "Onionr", message: str = ""):
    """Cross platform method to show a notification."""
    if not notifications_enabled:
        return
    simplenotify.notify(title, message)
