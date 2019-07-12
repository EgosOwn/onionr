'''
    Onionr - Private P2P Communication

    This file contains both the PeerProfiles class for network profiling of Onionr nodes
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
from . import scoresortedpeerlist, peercleanup
get_score_sorted_peer_list = scoresortedpeerlist.get_score_sorted_peer_list
peer_cleanup = peercleanup.peer_cleanup

class PeerProfiles:
    '''
        PeerProfiles
    '''
    def __init__(self, address, coreInst):
        self.address = address # node address
        self.score = None
        self.friendSigCount = 0
        self.success = 0
        self.failure = 0
        self.connectTime = None

        self.coreInst = coreInst

        self.loadScore()
        self.getConnectTime()
        return

    def loadScore(self):
        '''Load the node's score from the database'''
        try:
            self.success = int(self.coreInst.getAddressInfo(self.address, 'success'))
        except (TypeError, ValueError) as e:
            self.success = 0
        self.score = self.success
    
    def getConnectTime(self):
        try:
            self.connectTime = int(self.coreInst.getAddressInfo(self.address, 'lastConnect'))
        except (KeyError, ValueError, TypeError) as e:
            pass
        
    def saveScore(self):
        '''Save the node's score to the database'''
        self.coreInst.setAddressInfo(self.address, 'success', self.score)
        return

    def addScore(self, toAdd):
        '''Add to the peer's score (can add negative)'''
        self.score += toAdd
        self.saveScore()
