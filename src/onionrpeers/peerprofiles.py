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
from coredb import keydb
from onionrutils import epoch
from onionrutils import stringvalidators
from onionrblocks import onionrblacklist
import onionrexceptions

UPDATE_DELAY = 300

class PeerProfiles:
    '''
        PeerProfiles
    '''
    def __init__(self, address):
        if not stringvalidators.validate_transport(address): raise onionrexceptions.InvalidAddress
        self.address = address # node address
        self.score = None
        self.friendSigCount = 0
        self.success = 0
        self.failure = 0
        self.connectTime = None

        self.loadScore()
        self.getConnectTime()

        self.last_updated = {'connect_time': UPDATE_DELAY, 'score': UPDATE_DELAY} # Last time a given value was updated
        
        if not address in keydb.listkeys.list_adders() and not onionrblacklist.OnionrBlackList().inBlacklist(address):
            keydb.addkeys.add_address(address)

    def loadScore(self):
        '''Load the node's score from the database'''
        try:
            self.success = int(keydb.transportinfo.get_address_info(self.address, 'success'))
        except (TypeError, ValueError) as e:
            self.success = 0
        self.score = self.success
    
    def getConnectTime(self):
        """set the connectTime variable for when we last connected to them, using the db value"""
        try:
            self.connectTime = int(keydb.transportinfo.get_address_info(self.address, 'lastConnect'))
        except (KeyError, ValueError, TypeError) as e:
            pass
        else:
            return self.connectTime
    
    def update_connect_time(self):
        if epoch.get_epoch() - self.last_updated['connect_time'] >= UPDATE_DELAY:
            self.last_updated['connect_time'] = epoch.get_epoch()
            keydb.transportinfo.set_address_info(self.address, 'lastConnect', epoch.get_epoch())
        
    def saveScore(self):
        '''Save the node's score to the database'''
        if epoch.get_epoch() - self.last_updated['score'] >= UPDATE_DELAY:
            self.last_updated['score'] = epoch.get_epoch()
            keydb.transportinfo.set_address_info(self.address, 'success', self.score)
        return

    def addScore(self, toAdd):
        '''Add to the peer's score (can add negative)'''
        self.score += toAdd
        self.saveScore()
