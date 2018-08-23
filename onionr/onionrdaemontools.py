'''
    Onionr - P2P Microblogging Platform & Social network.

    Contains the CommunicatorUtils class which contains useful functions for the communicator daemon
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
import onionrexceptions, onionrpeers, onionrproofs, base64, logger
class DaemonTools:
    def __init__(self, daemon):
            self.daemon = daemon
            self.announceCache = {}

    def announceNode(self):
        '''Announce our node to our peers'''
        retData = False

        # Announce to random online peers
        for i in self.daemon.onlinePeers:
            if not i in self.announceCache:
                peer = i
                break
        else:
            peer = self.daemon.pickOnlinePeer()

        ourID = self.daemon._core.hsAddress.strip()

        url = 'http://' + peer + '/public/announce/'
        data = {'node': ourID}

        combinedNodes = ourID + peer

        if peer in self.announceCache:
            data['random'] = self.announceCache[peer]
        else:
            proof = onionrproofs.DataPOW(combinedNodes, forceDifficulty=4)
            data['random'] = base64.b64encode(proof.waitForResult()[1])
            self.announceCache[peer] = data['random']

        logger.info('Announcing node to ' + url)
        if self.daemon._core._utils.doPostRequest(url, data) == 'Success':
            retData = True
        self.daemon.decrementThreadCount('announceNode')
        return retData

    def netCheck(self):
        '''Check if we are connected to the internet or not when we can't connect to any peers'''
        if len(self.daemon.onlinePeers) != 0:
            if not self.daemon._core._utils.checkNetwork():
                logger.warn('Network check failed, are you connected to the internet?')
                self.daemon.isOnline = False
        self.daemon.decrementThreadCount('netCheck')
    
    def cleanOldBlocks(self):
        '''Delete old blocks if our disk allocation is full/near full'''
        if self.daemon._core._utils.storageCounter.isFull():
            
        
        self.daemon.decrementThreadCount('cleanOldBlocks')