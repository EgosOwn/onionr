'''
    Onionr - Private P2P Communication

    get online peers in a communicator instance
'''
'''
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
'''
import time
from etc import humanreadabletime
import logger
def get_online_peers(comm_inst):
    '''
        Manages the comm_inst.onlinePeers attribute list, connects to more peers if we have none connected
    '''
    config = comm_inst.config
    logger.debug('Refreshing peer pool...')
    maxPeers = int(config.get('peers.max_connect', 10))
    needed = maxPeers - len(comm_inst.onlinePeers)

    for i in range(needed):
        if len(comm_inst.onlinePeers) == 0:
            comm_inst.connectNewPeer(useBootstrap=True)
        else:
            comm_inst.connectNewPeer()

        if comm_inst.shutdown:
            break
    else:
        if len(comm_inst.onlinePeers) == 0:
            logger.debug('Couldn\'t connect to any peers.' + (' Last node seen %s ago.' % humanreadabletime.human_readable_time(time.time() - comm_inst.lastNodeSeen) if not comm_inst.lastNodeSeen is None else ''), terminal=True)
        else:
            comm_inst.lastNodeSeen = time.time()
    comm_inst.decrementThreadCount('get_online_peers')