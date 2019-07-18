'''
    Onionr - Private P2P Communication

    pick online peers in a communicator instance
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
import secrets
def pick_online_peer(comm_inst):
    '''randomly picks peer from pool without bias (using secrets module)'''
    retData = ''
    while True:
        peerLength = len(comm_inst.onlinePeers)
        if peerLength <= 0:
            break
        try:
            # get a random online peer, securely. May get stuck in loop if network is lost or if all peers in pool magically disconnect at once
            retData = comm_inst.onlinePeers[secrets.randbelow(peerLength)]
        except IndexError:
            pass
        else:
            break
    return retData