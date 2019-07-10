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
from . import onlinepeers
def peer_action(comm_inst, peer, action, data='', returnHeaders=False, max_resp_size=5242880):
    '''Perform a get request to a peer'''
    penalty_score = -10
    if len(peer) == 0:
        return False
    url = 'http://%s/%s' % (peer, action)
    if len(data) > 0:
        url += '&data=' + data

    comm_inst._core.setAddressInfo(peer, 'lastConnectAttempt', epoch.get_epoch()) # mark the time we're trying to request this peer
    try:
        retData = basicrequests.do_get_request(comm_inst._core, url, port=comm_inst.proxyPort, max_size=max_resp_size)
    except streamedrequests.exceptions.ResponseLimitReached:
        retData = False
        penalty_score = -100
    # if request failed, (error), mark peer offline
    if retData == False:
        try:
            comm_inst.getPeerProfileInstance(peer).addScore(penalty_score)
            comm_inst.removeOnlinePeer(peer)
            if action != 'ping' and not comm_inst.shutdown:
                logger.warn('Lost connection to ' + peer, terminal=True)
                onlinepeers.get_online_peers(comm_inst) # Will only add a new peer to pool if needed
        except ValueError:
            pass
    else:
        comm_inst._core.setAddressInfo(peer, 'lastConnect', epoch.get_epoch())
        comm_inst.getPeerProfileInstance(peer).addScore(1)
    return retData # If returnHeaders, returns tuple of data, headers. if not, just data string
