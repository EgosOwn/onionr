"""Onionr - Private P2P Communication.

clear offline peer in a communicator instance
"""
from typing import TYPE_CHECKING

import logger
if TYPE_CHECKING:
    from communicator import OnionrCommunicatorDaemon
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


def clear_offline_peer(kv: 'DeadSimpleKV'):
    """Remove the longest offline peer to retry later."""
    try:
        removed = kv.get('offlinePeers').pop(0)
    except IndexError:
        pass
    else:
        logger.debug('Removed ' + removed +
                     ' from offline list, will try them again.')

