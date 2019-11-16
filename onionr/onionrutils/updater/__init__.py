"""
    Onionr - Private P2P Communication

    Lib to keep Onionr up to date
"""
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
from onionrtypes import RestartRequiredStatus
from onionrblocks import onionrblockapi

from etc import onionrvalues
import onionrexceptions
import notifier

def update_event(bl)->RestartRequiredStatus:
    """Show update notification if available, return bool of if update happend"""
    if not bl.isSigner(onionrvalues.UPDATE_SIGN_KEY): raise onionrexceptions.InvalidUpdate
    notifier.notify(message="A new Onionr update is available. Stay updated to remain secure.")
