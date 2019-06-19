'''
    Onionr - Private P2P Communication

    Connect a new peer to our communicator instance. Does so randomly if no peer is specified
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
import time, sys
import onionrexceptions, logger, onionrpeers
from utils import networkmerger
# secrets module was added into standard lib in 3.6+
if sys.version_info[0] == 3 and sys.version_info[1] < 6:
    from dependencies import secrets
elif sys.version_info[0] == 3 and sys.version_info[1] >= 6:
    import secrets
def connect_new_peer_to_communicator(comm_inst, peer='', useBootstrap=False):
    config = comm_inst._core.config
    retData = False
    tried = comm_inst.offlinePeers
    if peer != '':
        if comm_inst._core._utils.validateID(peer):
            peerList = [peer]
        else:
            raise onionrexceptions.InvalidAddress('Will not attempt connection test to invalid address')
    else:
        peerList = comm_inst._core.listAdders()

    mainPeerList = comm_inst._core.listAdders()
    peerList = onionrpeers.getScoreSortedPeerList(comm_inst._core)

    # If we don't have enough peers connected or random chance, select new peers to try
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
        comm_inst.addBootstrapListToPeerList(peerList)

    for address in peerList:
        if not config.get('tor.v3onions') and len(address) == 62:
            continue
        # Don't connect to our own address
        if address == comm_inst._core.hsAddress:
            continue
        # Don't connect to invalid address or if its already been tried/connected, or if its cooled down
        if len(address) == 0 or address in tried or address in comm_inst.onlinePeers or address in comm_inst.cooldownPeer:
            continue
        if comm_inst.shutdown:
            return
        # Ping a peer,
        if comm_inst.peerAction(address, 'ping') == 'pong!':
            time.sleep(0.1)
            if address not in mainPeerList:
                # Add a peer to our list if it isn't already since it successfully connected
                networkmerger.mergeAdders(address, comm_inst._core)
            if address not in comm_inst.onlinePeers:
                logger.info('Connected to ' + address, terminal=True)
                comm_inst.onlinePeers.append(address)
                comm_inst.connectTimes[address] = comm_inst._core._utils.getEpoch()
            retData = address

            # add peer to profile list if they're not in it
            for profile in comm_inst.peerProfiles:
                if profile.address == address:
                    break
            else:
                comm_inst.peerProfiles.append(onionrpeers.PeerProfiles(address, comm_inst._core))
            break
        else:
            # Mark a peer as tried if they failed to respond to ping
            tried.append(address)
            logger.debug('Failed to connect to ' + address)
    return retData