'''
    Onionr - P2P Anonymous Storage Network

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
import onionrexceptions, onionrpeers, onionrproofs, base64, logger, onionrusers, sqlite3
from dependencies import secrets
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
            logger.info('Successfully introduced node to ' + peer)
            retData = True
        self.daemon.decrementThreadCount('announceNode')
        return retData

    def netCheck(self):
        '''Check if we are connected to the internet or not when we can't connect to any peers'''
        if len(self.daemon.onlinePeers) == 0:
            if not self.daemon._core._utils.checkNetwork(torPort=self.daemon.proxyPort):
                logger.warn('Network check failed, are you connected to the internet?')
                self.daemon.isOnline = False
        self.daemon.decrementThreadCount('netCheck')

    def cleanOldBlocks(self):
        '''Delete old blocks if our disk allocation is full/near full, and also expired blocks'''

        while self.daemon._core._utils.storageCounter.isFull():
            oldest = self.daemon._core.getBlockList()[0]
            self.daemon._core._blacklist.addToDB(oldest)
            self.daemon._core.removeBlock(oldest)
            logger.info('Deleted block: %s' % (oldest,))

        # Delete expired blocks
        for bHash in self.daemon._core.getExpiredBlocks():
            self.daemon._core._blacklist.addToDB(bHash)
            self.daemon._core.removeBlock(bHash)

        self.daemon.decrementThreadCount('cleanOldBlocks')

    def cleanKeys(self):
        '''Delete expired forward secrecy keys'''
        conn = sqlite3.connect(self.daemon._core.peerDB, timeout=10)
        c = conn.cursor()
        time = self.daemon._core._utils.getEpoch()
        deleteKeys = []
        for entry in c.execute("SELECT * FROM forwardKeys WHERE expire <= ?", (time,)):
            logger.info(entry[1])
            deleteKeys.append(entry[1])

        for key in deleteKeys:
            logger.info('Deleting forward key '+ key)
            c.execute("DELETE from forwardKeys where forwardKey = ?", (key,))
        conn.commit()
        conn.close()

        onionrusers.deleteExpiredKeys(self.daemon._core)

        self.daemon.decrementThreadCount('cleanKeys')

    def cooldownPeer(self):
        '''Randomly add an online peer to cooldown, so we can connect a new one'''
        onlinePeerAmount = len(self.daemon.onlinePeers)
        minTime = 300
        cooldownTime = 600
        toCool = ''
        tempConnectTimes = dict(self.daemon.connectTimes)

        # Remove peers from cooldown that have been there long enough
        tempCooldown = dict(self.daemon.cooldownPeer)
        for peer in tempCooldown:
            if (self.daemon._core._utils.getEpoch() - tempCooldown[peer]) >= cooldownTime:
                del self.daemon.cooldownPeer[peer]

        # Cool down a peer, if we have max connections alive for long enough
        if onlinePeerAmount >= self.daemon._core.config.get('peers.max_connect', 10):
            finding = True
            while finding:
                try:
                    toCool = min(tempConnectTimes, key=tempConnectTimes.get)
                    if (self.daemon._core._utils.getEpoch() - tempConnectTimes[toCool]) < minTime:
                        del tempConnectTimes[toCool]
                    else:
                        finding = False
                except ValueError:
                    break
            else:
                self.daemon.removeOnlinePeer(toCool)
                self.daemon.cooldownPeer[toCool] = self.daemon._core._utils.getEpoch()
        self.daemon.decrementThreadCount('cooldownPeer')
