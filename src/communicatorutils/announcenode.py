"""
    Onionr - Private P2P Communication.

Use a communicator instance to announce
our transport address to connected nodes
"""
import base64
import onionrproofs
import logger
from etc import onionrvalues
from onionrutils import basicrequests, bytesconverter
from utils import gettransports
from netcontroller import NetController
from communicator import onlinepeers
from coredb import keydb
import onionrexceptions
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


def announce_node(daemon):
    """Announce our node to our peers."""
    ret_data = False
    announce_fail = False

    # Do not let announceCache get too large
    if len(daemon.announceCache) >= 10000:
        daemon.announceCache.popitem()

    if daemon.config.get('general.security_level', 0) == 0:
        # Announce to random online peers
        for i in daemon.onlinePeers:
            if i not in daemon.announceCache and\
                    i not in daemon.announceProgress:
                peer = i
                break
        else:
            try:
                peer = onlinepeers.pick_online_peer(daemon)
            except onionrexceptions.OnlinePeerNeeded:
                peer = ""

        for _ in range(1):
            try:
                ourID = gettransports.get()[0]
                if not peer:
                    raise onionrexceptions.OnlinePeerNeeded
            except (IndexError, onionrexceptions.OnlinePeerNeeded):
                break

            url = 'http://' + peer + '/announce'
            data = {'node': ourID}

            combinedNodes = ourID + peer
            if ourID != 1:
                existingRand = bytesconverter.bytes_to_str(
                    keydb.transportinfo.get_address_info(peer, 'powValue'))
                # Reset existingRand if it no longer meets the minimum POW
                if isinstance(existingRand, type(None)) or \
                    not existingRand.endswith(
                        '0' * onionrvalues.ANNOUNCE_POW):
                    existingRand = ''

            if peer in daemon.announceCache:
                data['random'] = daemon.announceCache[peer]
            elif len(existingRand) > 0:
                data['random'] = existingRand
            else:
                daemon.announceProgress[peer] = True
                proof = onionrproofs.DataPOW(
                    combinedNodes, minDifficulty=onionrvalues.ANNOUNCE_POW)
                del daemon.announceProgress[peer]
                try:
                    data['random'] = base64.b64encode(proof.waitForResult()[1])
                except TypeError:
                    # Happens when we failed to produce a proof
                    logger.error(f"Failed to produce a pow for {peer} annce")
                    announce_fail = True
                else:
                    daemon.announceCache[peer] = data['random']
            if not announce_fail:
                logger.info('Announcing node to ' + url)
                if basicrequests.do_post_request(
                        url,
                        data,
                        port=daemon.shared_state.get(NetController).socksPort)\
                        == 'Success':
                    logger.info('Successfully introduced node to ' + peer,
                                terminal=True)
                    ret_data = True
                    keydb.transportinfo.set_address_info(peer, 'introduced', 1)
                    keydb.transportinfo.set_address_info(peer, 'powValue',
                                                         data['random'])
    daemon.decrementThreadCount('announce_node')
    return ret_data
