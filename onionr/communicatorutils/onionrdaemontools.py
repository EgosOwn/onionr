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

import onionrexceptions, onionrpeers, onionrproofs, logger
import base64, sqlite3, os
from dependencies import secrets
from utils import netutils
from onionrusers import onionrusers

class DaemonTools:
    '''
        Class intended for use by Onionr Communicator
    '''
    def __init__(self, daemon):
            self.daemon = daemon
            self.announceProgress = {}
            self.announceCache = {}

    def announceNode(self):
        '''Announce our node to our peers'''
        retData = False
        announceFail = False
        
        # Do not let announceCache get too large
        if len(self.announceCache) >= 10000:
            self.announceCache.popitem()

        if self.daemon._core.config.get('general.security_level', 0) == 0:
            # Announce to random online peers
            for i in self.daemon.onlinePeers:
                if not i in self.announceCache and not i in self.announceProgress:
                    peer = i
                    break
            else:
                peer = self.daemon.pickOnlinePeer()

            for x in range(1):
                if x == 1 and self.daemon._core.config.get('i2p.host'):
                    ourID = self.daemon._core.config.get('i2p.own_addr').strip()
                else:
                    ourID = self.daemon._core.hsAddress.strip()

                url = 'http://' + peer + '/announce'
                data = {'node': ourID}

                combinedNodes = ourID + peer
                if ourID != 1:
                    #TODO: Extend existingRand for i2p
                    existingRand = self.daemon._core.getAddressInfo(peer, 'powValue')
                    if type(existingRand) is type(None):
                        existingRand = ''

                if peer in self.announceCache:
                    data['random'] = self.announceCache[peer]
                elif len(existingRand) > 0:
                    data['random'] = existingRand
                else:
                    self.announceProgress[peer] = True
                    proof = onionrproofs.DataPOW(combinedNodes, forceDifficulty=4)
                    del self.announceProgress[peer]
                    try:
                        data['random'] = base64.b64encode(proof.waitForResult()[1])
                    except TypeError:
                        # Happens when we failed to produce a proof
                        logger.error("Failed to produce a pow for announcing to " + peer)
                        announceFail = True
                    else:
                        self.announceCache[peer] = data['random']
                if not announceFail:
                    logger.info('Announcing node to ' + url)
                    if self.daemon._core._utils.doPostRequest(url, data) == 'Success':
                        logger.info('Successfully introduced node to ' + peer)
                        retData = True
                        self.daemon._core.setAddressInfo(peer, 'introduced', 1)
                        self.daemon._core.setAddressInfo(peer, 'powValue', data['random'])
        self.daemon.decrementThreadCount('announceNode')
        return retData

    def netCheck(self):
        '''Check if we are connected to the internet or not when we can't connect to any peers'''
        if len(self.daemon.onlinePeers) == 0:
            if not netutils.checkNetwork(self.daemon._core._utils, torPort=self.daemon.proxyPort):
                if not self.daemon.shutdown:
                    logger.warn('Network check failed, are you connected to the internet?')
                self.daemon.isOnline = False
            else:
                self.daemon.isOnline = True
        self.daemon.decrementThreadCount('netCheck')

    def cleanOldBlocks(self):
        '''Delete old blocks if our disk allocation is full/near full, and also expired blocks'''

        # Delete expired blocks
        for bHash in self.daemon._core.getExpiredBlocks():
            self.daemon._core._blacklist.addToDB(bHash)
            self.daemon._core.removeBlock(bHash)
            logger.info('Deleted block: %s' % (bHash,))

        while self.daemon._core._utils.storageCounter.isFull():
            oldest = self.daemon._core.getBlockList()[0]
            self.daemon._core._blacklist.addToDB(oldest)
            self.daemon._core.removeBlock(oldest)
            logger.info('Deleted block: %s' % (oldest,))

        self.daemon.decrementThreadCount('cleanOldBlocks')

    def cleanKeys(self):
        '''Delete expired forward secrecy keys'''
        conn = sqlite3.connect(self.daemon._core.peerDB, timeout=10)
        c = conn.cursor()
        time = self.daemon._core._utils.getEpoch()
        deleteKeys = []

        for entry in c.execute("SELECT * FROM forwardKeys WHERE expire <= ?", (time,)):
            logger.debug('Forward key: %s' % entry[1])
            deleteKeys.append(entry[1])

        for key in deleteKeys:
            logger.debug('Deleting forward key %s' % key)
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
        if onlinePeerAmount >= self.daemon._core.config.get('peers.max_connect', 10, save = True):
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

    def runCheck(self):
        if os.path.isfile(self.daemon._core.dataDir + '.runcheck'):
            os.remove(self.daemon._core.dataDir + '.runcheck')
            return True

        return False

    def humanReadableTime(self, seconds):
        build = ''

        units = {
            'year' : 31557600,
            'month' : (31557600 / 12),
            'day' : 86400,
            'hour' : 3600,
            'minute' : 60,
            'second' : 1
        }

        for unit in units:
            amnt_unit = int(seconds / units[unit])
            if amnt_unit >= 1:
                seconds -= amnt_unit * units[unit]
                build += '%s %s' % (amnt_unit, unit) + ('s' if amnt_unit != 1 else '') + ' '

        return build.strip()

    def insertDeniableBlock(self):
        '''Insert a fake block in order to make it more difficult to track real blocks'''
        fakePeer = ''
        chance = 10
        if secrets.randbelow(chance) == (chance - 1):
            fakePeer = 'OVPCZLOXD6DC5JHX4EQ3PSOGAZ3T24F75HQLIUZSDSMYPEOXCPFA===='
            data = secrets.token_hex(secrets.randbelow(500) + 1)
            self.daemon._core.insertBlock(data, header='pm', encryptType='asym', asymPeer=fakePeer, meta={'subject': 'foo'})
        self.daemon.decrementThreadCount('insertDeniableBlock')
        return