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


def connect_new_peer_to_communicator(comm_inst, peer='', useBootstrap=False):
    config = comm_inst.config
    retData = False
    tried = comm_inst.offlinePeers
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
    peerList = onionrpeers.get_score_sorted_peer_list()

    """
    If we don't have enough peers connected or random chance,
    select new peers to try
    """
    if len(peerList) < 8 or secrets.randbelow(4) == 3:
        tryingNew = []
        for x in comm_inst.newPeers:
            if x not in peerList:
                peerList.append(x)
                tryingNew.append(x)
        for i in tryingNew:
            comm_inst.newPeers.remove(i)

    if len(peerList) == 0 or useBootstrap:
        # Avoid duplicating bootstrap addresses in peerList
        if config.get('general.use_bootstrap_list', True):
            bootstrappeers.add_bootstrap_list_to_peer_list(comm_inst, peerList)

    for address in peerList:
        address = address.strip()

        # Don't connect to our own address
        if address in transports:
            continue
        """Don't connect to invalid address or
        if its already been tried/connected, or if its cooled down
        """
        if len(address) == 0 or address in tried \
            or address in comm_inst.onlinePeers \
                or address in comm_inst.cooldownPeer:
            continue
        if comm_inst.shutdown:
            return
        # Ping a peer,
        ret = peeraction.peer_action(comm_inst, address, 'ping')
        if ret == 'pong!':
            time.sleep(0.1)
            if address not in mainPeerList:
                # Add a peer to our list if it isn't already since it connected
                networkmerger.mergeAdders(address)
            if address not in comm_inst.onlinePeers:
                logger.info('Connected to ' + address, terminal=True)
                comm_inst.onlinePeers.append(address)
                comm_inst.connectTimes[address] = epoch.get_epoch()
            retData = address

            # add peer to profile list if they're not in it
            for profile in comm_inst.peerProfiles:
                if profile.address == address:
                    break
            else:
                comm_inst.peerProfiles.append(
                    onionrpeers.PeerProfiles(address))
            break
        else:
            # Mark a peer as tried if they failed to respond to ping
            tried.append(address)
            logger.debug('Failed to connect to %s: %s ' % (address, ret))
    return retData
