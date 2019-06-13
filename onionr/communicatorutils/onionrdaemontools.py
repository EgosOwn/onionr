'''
    Onionr - Private P2P Communication

    Contains the DaemonTools class
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

# MODULE DEPRECATED

import onionrexceptions, onionrpeers, onionrproofs, logger
import base64, sqlite3, os
from dependencies import secrets
from utils import netutils
from onionrusers import onionrusers
from etc import onionrvalues
ov = onionrvalues.OnionrValues()

class DaemonTools:
    '''
        Class intended for use by Onionr Communicator
    '''
    def __init__(self, daemon):
            self.daemon = daemon
            self.announceProgress = {}
            self.announceCache = {}

    def netCheck(self):
        '''Check if we are connected to the internet or not when we can't connect to any peers'''
        if len(self.daemon.onlinePeers) == 0:
            if not netutils.checkNetwork(self.daemon._core._utils, torPort=self.daemon.proxyPort):
                if not self.daemon.shutdown:
                    logger.warn('Network check failed, are you connected to the Internet, and is Tor working?')
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
            # This assumes on the libsodium primitives to have key-privacy
            fakePeer = 'OVPCZLOXD6DC5JHX4EQ3PSOGAZ3T24F75HQLIUZSDSMYPEOXCPFA===='
            data = secrets.token_hex(secrets.randbelow(1024) + 1)
            self.daemon._core.insertBlock(data, header='pm', encryptType='asym', asymPeer=fakePeer, meta={'subject': 'foo'})
        self.daemon.decrementThreadCount('insertDeniableBlock')