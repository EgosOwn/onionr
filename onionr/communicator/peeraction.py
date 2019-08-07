'''
    Onionr - Private P2P Communication

    This file implements logic for performing requests to Onionr peers
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
import streamedrequests
import logger
from onionrutils import epoch, basicrequests
from coredb import keydb
from . import onlinepeers
def peer_action(comm_inst, peer, action, returnHeaders=False, max_resp_size=5242880):
    '''Perform a get request to a peer'''
    penalty_score = -10
    if not peer:
        return False
    url = 'http://%s/%s' % (peer, action)

    # mark the time we're trying to request this peer
    keydb.transportinfo.set_address_info(peer, 'lastConnectAttempt', epoch.get_epoch())

    try:
        ret_data = basicrequests.do_get_request(url, port=comm_inst.proxyPort,
                                                max_size=max_resp_size)
    except streamedrequests.exceptions.ResponseLimitReached:
        logger.warn('Request failed due to max response size being overflowed', terminal=True)
        ret_data = False
        penalty_score = -100
    # if request failed, (error), mark peer offline
    if not ret_data:
        try:
            comm_inst.getPeerProfileInstance(peer).addScore(penalty_score)
            onlinepeers.remove_online_peer(comm_inst, peer)
            if action != 'ping' and not comm_inst.shutdown:
                logger.warn('Lost connection to ' + peer, terminal=True)
                onlinepeers.get_online_peers(comm_inst) # Will only add a new peer to pool if needed
        except ValueError:
            pass
    else:
        peer_profile = comm_inst.getPeerProfileInstance(peer)
        peer_profile.update_connect_time()
        peer_profile.addScore(1)
    return ret_data # If returnHeaders, returns tuple of data, headers. if not, just data string
