"""Onionr - Private P2P Communication.

Connect a new peer to our communicator instance.
Does so randomly if no peer is specified
"""
import time
import secrets

import onionrexceptions
import logger
import onionrpeers
from utils import networkmerger, gettransports
from onionrutils import stringvalidators, epoch
from communicator import peeraction, bootstrappeers
from coredb import keydb
import config
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


def connect_new_peer_to_communicator(shared_state, peer='', useBootstrap=False):
    retData = False
    kv: "DeadSimpleKV" = shared_state.get_by_string("DeadSimpleKV")
    tried = kv.get('offlinePeers')
    transports = gettransports.get()
    if peer != '':
        if stringvalidators.validate_transport(peer):
            peerList = [peer]
        else:
            raise onionrexceptions.InvalidAddress(
                'Will not attempt connection test to invalid address')
    else:
        peerList = keydb.listkeys.list_adders()

    mainPeerList = keydb.listkeys.list_adders()
    if not peerList:
        peerList = onionrpeers.get_score_sorted_peer_list()

    """
    If we don't have enough peers connected or random chance,
    select new peers to try
    """
    if len(peerList) < 8 or secrets.randbelow(4) == 3:
        tryingNew = []
        for x in kv.get('newPeers'):
            if x not in peerList:
                peerList.append(x)
                tryingNew.append(x)
        for i in tryingNew:
            kv.get('newPeers').remove(i)

    if len(peerList) == 0 or useBootstrap:
        # Avoid duplicating bootstrap addresses in peerList
        if config.get('general.use_bootstrap_list', True):
            bootstrappeers.add_bootstrap_list_to_peer_list(kv, peerList)

    for address in peerList:
        address = address.strip()

        # Don't connect to our own address
        if address in transports:
            continue
        """Don't connect to invalid address or
        if its already been tried/connected, or if its cooled down
        """
        if len(address) == 0 or address in tried \
            or address in kv.get('onlinePeers') \
                or address in kv.get('cooldownPeer'):
            continue
        if kv.get('shutdown'):
            return
        # Ping a peer,
        ret = peeraction.peer_action(shared_state, address, 'ping')
        if ret == 'pong!':
            time.sleep(0.1)
            if address not in mainPeerList:
                # Add a peer to our list if it isn't already since it connected
                networkmerger.mergeAdders(address)
            if address not in kv.get('onlinePeers'):
                logger.info('Connected to ' + address, terminal=True)
                kv.get('onlinePeers').append(address)
                kv.get('connectTimes')[address] = epoch.get_epoch()
            retData = address

            # add peer to profile list if they're not in it
            for profile in kv.get('peerProfiles'):
                if profile.address == address:
                    break
            else:
                kv.get('peerProfiles').append(
                    onionrpeers.PeerProfiles(address))
            try:
                del kv.get('plaintextDisabledPeers')[address]
            except KeyError:
                pass
            if peeraction.peer_action(
                    shared_state, address, 'plaintext') == 'false':
                kv.get('plaintextDisabledPeers')[address] = True
            break

        else:
            # Mark a peer as tried if they failed to respond to ping
            tried.append(address)
            logger.debug('Failed to connect to %s: %s ' % (address, ret))
    return retData
