'''
    Onionr - P2P Anonymous Storage Network

    Lookup new peer transport addresses using the communicator
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
import logger

def lookup_new_peer_transports_with_communicator(comm_inst):
    logger.info('Looking up new addresses...')
    tryAmount = 1
    newPeers = []
    for i in range(tryAmount):
        # Download new peer address list from random online peers
        if len(newPeers) > 10000:
            # Dont get new peers if we have too many queued up
            break
        peer = comm_inst.pickOnlinePeer()
        newAdders = comm_inst.peerAction(peer, action='pex')
        try:
            newPeers = newAdders.split(',')
        except AttributeError:
            pass
    else:
        # Validate new peers are good format and not already in queue
        invalid = []
        for x in newPeers:
            x = x.strip()
            if not comm_inst._core._utils.validateID(x) or x in comm_inst.newPeers or x == comm_inst._core.hsAddress:
                # avoid adding if its our address
                invalid.append(x)
        for x in invalid:
            newPeers.remove(x)
        comm_inst.newPeers.extend(newPeers)
    comm_inst.decrementThreadCount('lookupAdders')