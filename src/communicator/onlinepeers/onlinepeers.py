"""Onionr - Private P2P Communication.

get online peers in a communicator instance
"""
import time
from typing import TYPE_CHECKING

import config
from etc.humanreadabletime import human_readable_time
from communicatorutils.connectnewpeers import connect_new_peer_to_communicator
import logger
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


def get_online_peers(shared_state):
    """Manage the kv.get('onlinePeers') attribute list.

    Connect to more peers if we have none connected
    """
    kv: "DeadSimpleKV" = shared_state.get_by_string("DeadSimpleKV")
    if config.get('general.offline_mode', False):
        return
    logger.info('Refreshing peer pool...')
    max_peers = int(config.get('peers.max_connect', 10))
    needed = max_peers - len(kv.get('onlinePeers'))

    last_seen = 'never'
    if not isinstance(kv.get('lastNodeSeen'), type(None)):
        last_seen = human_readable_time(kv.get('lastNodeSeen'))

    for _ in range(needed):
        if len(kv.get('onlinePeers')) == 0:
            connect_new_peer_to_communicator(shared_state, useBootstrap=True)
        else:
            connect_new_peer_to_communicator(shared_state)

        if kv.get('shutdown'):
            break
    else:
        if len(kv.get('onlinePeers')) == 0:
            logger.debug('Couldn\'t connect to any peers.' +
                         f' Last node seen {last_seen}  ago.')
            try:
                get_online_peers(shared_state)
            except RecursionError:
                pass
        else:
            kv.put('lastNodeSeen', time.time())
