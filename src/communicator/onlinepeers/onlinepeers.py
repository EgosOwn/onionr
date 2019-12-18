"""
    Onionr - Private P2P Communication

    get online peers in a communicator instance
"""
import time
from etc import humanreadabletime
import logger
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


def get_online_peers(comm_inst):
    """
        Manages the comm_inst.onlinePeers attribute list,
        ]connects to more peers if we have none connected
    """
    config = comm_inst.config
    if config.get('general.offline_mode', False):
        comm_inst.decrementThreadCount('get_online_peers')
        return
    logger.debug('Refreshing peer pool...')
    maxPeers = int(config.get('peers.max_connect', 10))
    needed = maxPeers - len(comm_inst.onlinePeers)

    last_seen = 'never'
    if not isinstance(comm_inst.lastNodeSeen, None):
        last_seen = humanreadabletime.human_readable_time(
            comm_inst.lastNodeSeen)

    for i in range(needed):
        if len(comm_inst.onlinePeers) == 0:
            comm_inst.connectNewPeer(useBootstrap=True)
        else:
            comm_inst.connectNewPeer()

        if comm_inst.shutdown:
            break
    else:
        if len(comm_inst.onlinePeers) == 0:
            logger.debug
            ('Couldn\'t connect to any peers.' +
             f' Last node seen {last_seen}  ago.')
        else:
            comm_inst.lastNodeSeen = time.time()
    comm_inst.decrementThreadCount('get_online_peers')
