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
import sqlite3
import core, config, logger
config.reload()
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

        if not isinstance(coreInst, core.Core):
            raise TypeError("coreInst must be a type of core.Core")
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

def getScoreSortedPeerList(coreInst):
    if not type(coreInst is core.Core):
        raise TypeError('coreInst must be instance of core.Core')

    peerList = coreInst.listAdders()
    peerScores = {}
    peerTimes = {}

    for address in peerList:
        # Load peer's profiles into a list
        profile = PeerProfiles(address, coreInst)
        peerScores[address] = profile.score
        if not isinstance(profile.connectTime, type(None)):
            peerTimes[address] = profile.connectTime
        else:
            peerTimes[address] = 9000

    # Sort peers by their score, greatest to least, and then last connected time
    peerList = sorted(peerScores, key=peerScores.get, reverse=True)
    peerList = sorted(peerTimes, key=peerTimes.get, reverse=True)
    return peerList

def peerCleanup(coreInst):
    '''Removes peers who have been offline too long or score too low'''
    if not type(coreInst is core.Core):
        raise TypeError('coreInst must be instance of core.Core')

    logger.info('Cleaning peers...')

    adders = getScoreSortedPeerList(coreInst)
    adders.reverse()
    
    if len(adders) > 1:

        minScore = int(config.get('peers.minimum_score', -100))
        maxPeers = int(config.get('peers.max_stored', 5000))

        for address in adders:
            # Remove peers that go below the negative score
            if PeerProfiles(address, coreInst).score < minScore:
                coreInst.removeAddress(address)
                try:
                    if (int(coreInst._utils.getEpoch()) - int(coreInst.getPeerInfo(address, 'dateSeen'))) >= 600:
                        expireTime = 600
                    else:
                        expireTime = 86400
                    coreInst._blacklist.addToDB(address, dataType=1, expire=expireTime)
                except sqlite3.IntegrityError: #TODO just make sure its not a unique constraint issue
                    pass
                except ValueError:
                    pass
                logger.warn('Removed address ' + address + '.')

    # Unban probably not malicious peers TODO improve
    coreInst._blacklist.deleteExpired(dataType=1)
