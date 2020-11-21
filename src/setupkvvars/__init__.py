"""Onionr - Private P2P Communication.

Initialize singleton deadsimplekv pseudo globals
"""

from typing import TYPE_CHECKING

from onionrutils import epoch

if TYPE_CHECKING:
    from deadsimplekv import DeadSimpleKV
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


def setup_kv(shared_vars: 'DeadSimpleKV'):
    """Init initial pseudo-globals."""
    shared_vars.put('plaintextDisabledPeers', {})
    shared_vars.put('blockQueue', {})
    shared_vars.put('shutdown', False)
    shared_vars.put('onlinePeers', [])
    shared_vars.put('offlinePeers', [])
    shared_vars.put('peerProfiles', [])
    shared_vars.put('connectTimes', {})
    shared_vars.put('currentDownloading', [])
    shared_vars.put('announceCache', {})
    shared_vars.put('newPeers', [])
    shared_vars.put('dbTimestamps', {})
    shared_vars.put('blocksToUpload', [])
    shared_vars.put('cooldownPeer', {})
    shared_vars.put('generating_blocks', [])
    shared_vars.put('lastNodeSeen', None)
    shared_vars.put('startTime', epoch.get_epoch())
    shared_vars.put('isOnline', True)
