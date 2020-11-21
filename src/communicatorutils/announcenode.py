"""
Onionr - Private P2P Communication.

Use a communicator instance to announce
our transport address to connected nodes
"""
from typing import TYPE_CHECKING

import logger
from onionrutils import basicrequests
from utils import gettransports
from netcontroller import NetController
from communicator import onlinepeers
from coredb import keydb
import onionrexceptions

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


def announce_node(shared_state):
    """Announce our node to our peers."""
    ret_data = False
    kv: "DeadSimpleKV" = shared_state.get_by_string("DeadSimpleKV")
    config = shared_state.get_by_string("OnionrCommunicatorDaemon").config
    # Do not let announceCache get too large
    if len(kv.get('announceCache')) >= 10000:
        kv.get('announceCache').popitem()

    if config.get('general.security_level', 0) == 0:
        # Announce to random online peers
        for i in kv.get('onlinePeers'):
            if i not in kv.get('announceCache'):
                peer = i
                break
        else:
            try:
                peer = onlinepeers.pick_online_peer(kv)
            except onionrexceptions.OnlinePeerNeeded:
                peer = ""

        try:
            ourID = gettransports.get()[0]
            if not peer:
                raise onionrexceptions.OnlinePeerNeeded
        except (IndexError, onionrexceptions.OnlinePeerNeeded):
            pass
        else:
            url = 'http://' + peer + '/announce'
            data = {'node': ourID}

            logger.info('Announcing node to ' + url)
            if basicrequests.do_post_request(
                    url,
                    data,
                    port=shared_state.get(NetController).socksPort)\
                    == 'Success':
                logger.info('Successfully introduced node to ' + peer,
                            terminal=True)
                ret_data = True
                keydb.transportinfo.set_address_info(peer, 'introduced', 1)

    return ret_data
