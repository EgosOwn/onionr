#!/usr/bin/env python3
'''
Onionr - P2P Microblogging Platform & Social network.

This file contains both the OnionrCommunicate class for communcating with peers
and code to operate as a daemon, getting commands from the command queue database (see core.Core.daemonQueue)
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
import sqlite3, requests, hmac, hashlib, time, sys, os, math, logger, urllib.parse, base64, binascii, random
import core, onionrutils, onionrcrypto, netcontroller, onionrproofs, btc, config, onionrplugins as plugins

class OnionrCommunicate:
    def __init__(self, debug, developmentMode):
        '''
            OnionrCommunicate

            This class handles communication with nodes in the Onionr network.
        '''

        self._core = core.Core()
        self._utils = onionrutils.OnionrUtils(self._core)
        self._crypto = onionrcrypto.OnionrCrypto(self._core)
        self._netController = netcontroller.NetController(0) # arg is the HS port but not needed rn in this file

        self.newHashes = {} # use this to not keep hashes around too long if we cant get their data
        self.keepNewHash = 12
        self.ignoredHashes = []

        self.highFailureAmount = 7
        '''
        logger.info('Starting Bitcoin Node... with Tor socks port:' + str(sys.argv[2]), timestamp=True)
        try:
            self.bitcoin = btc.OnionrBTC(torP=int(sys.argv[2]))
        except _gdbm.error:
            pass
        logger.info('Bitcoin Node started, on block: ' + self.bitcoin.node.getBlockHash(self.bitcoin.node.getLastBlockHeight()), timestamp=True)
        '''
        #except:
        #logger.fatal('Failed to start Bitcoin Node, exiting...')
        #exit(1)

        blockProcessTimer = 0
        blockProcessAmount = 5
        highFailureTimer = 0
        highFailureRate = 10
        heartBeatTimer = 0
        heartBeatRate = 0
        pexTimer = 25 # How often we should check for new peers
        pexCount = 0
        logger.debug('Communicator debugging enabled.')
        torID = open('data/hs/hostname').read()

        apiRunningCheckRate = 10
        apiRunningCheckCount = 0

        self.peerData = {} # Session data for peers (recent reachability, speed, etc)

        if os.path.exists(self._core.queueDB):
            self._core.clearDaemonQueue()

        # Loads in and starts the enabled plugins
        plugins.reload()

        while True:
            command = self._core.daemonQueue()
            # Process blocks based on a timer
            blockProcessTimer += 1
            heartBeatTimer += 1
            pexCount += 1
            if highFailureTimer == highFailureRate:
                highFailureTimer = 0
                for i in self.peerData:
                    if self.peerData[i]['failCount'] == self.highFailureAmount:
                        self.peerData[i]['failCount'] -= 1
            if pexTimer == pexCount:
                self.getNewPeers()
                pexCount = 0 # TODO: do not reset timer if low peer count
            if heartBeatRate == heartBeatTimer:
                logger.debug('Communicator heartbeat')
                heartBeatTimer = 0
            if blockProcessTimer == blockProcessAmount:
                self.lookupBlocks()
                self.processBlocks()
                blockProcessTimer = 0
            if command != False:
                if command[0] == 'shutdown':
                    logger.info('Daemon recieved exit command.', timestamp=True)
                    break
                elif command[0] == 'announceNode':
                    announceAttempts = 3
                    announceAttemptCount = 0
                    announceVal = False
                    logger.info('Announcing our node to ' + command[1], timestamp=True)
                    while not announceVal:
                        announceAttemptCount += 1
                        announceVal = self.performGet('announce', command[1], data=self._core.hsAdder.replace('\n', ''), skipHighFailureAddress=True)
                        logger.info(announceVal)
                        if announceAttemptCount >= announceAttempts:
                            logger.warn('Unable to announce to ' + command[1])
                            break
            apiRunningCheckCount += 1
            # check if local API is up
            if apiRunningCheckCount > apiRunningCheckRate:
                if self._core._utils.localCommand('ping') != 'pong':
                    for i in range(4):
                        if self._utils.localCommand('ping') == 'pong':
                            apiRunningCheckCount = 0
                            break # break for loop
                        time.sleep(1)
                    else:
                        # This executes if the api is NOT detected to be running
                        logger.error('Daemon detected API crash (or otherwise unable to reach API after long time, stopping)')
                        break # break main daemon loop
                apiRunningCheckCount = 0

            time.sleep(1)
        self._netController.killTor()
        return

    def getNewPeers(self):
        '''
            Get new peers and keys
        '''
        peersCheck = 5 # Amount of peers to ask for new peers + keys
        peersChecked = 0
        peerList = list(self._core.listAdders()) # random ordered list of peers
        newKeys = []
        newAdders = []
        if len(peerList) > 0:
            maxN = len(peerList) - 1
        else:
            peersCheck = 0
            maxN = 0

        if len(peerList) > peersCheck:
            peersCheck = len(peerList)

        while peersCheck > peersChecked:
            #i = secrets.randbelow(maxN) # cant use prior to 3.6
            i = random.randint(0, maxN)
            logger.info('Using ' + peerList[i] + ' to find new peers', timestamp=True)
            try:
                newAdders = self.performGet('pex', peerList[i], skipHighFailureAddress=True)
                logger.debug('Attempting to merge address: ')
                logger.debug(newAdders)
                self._utils.mergeAdders(newAdders)
            except requests.exceptions.ConnectionError:
                logger.info(peerList[i] + ' connection failed', timestamp=True)
                continue
            else:
                try:
                    logger.info('Using ' + peerList[i] + ' to find new keys')
                    newKeys = self.performGet('kex', peerList[i], skipHighFailureAddress=True)
                    logger.debug('Attempting to merge pubkey: ')
                    logger.debug(newKeys)
                    # TODO: Require keys to come with POW token (very large amount of POW)
                    self._utils.mergeKeys(newKeys)
                except requests.exceptions.ConnectionError:
                    logger.info(peerList[i] + ' connection failed', timestamp=True)
                    continue
                else:
                    peersChecked += 1
        return

    def lookupBlocks(self):
        '''
            Lookup blocks and merge new ones
        '''
        peerList = self._core.listAdders()
        blocks = ''
        for i in peerList:
            try:
                if self.peerData[i]['failCount'] >= self.highFailureAmount:
                    continue
            except KeyError:
                pass
            lastDB = self._core.getAddressInfo(i, 'DBHash')
            if lastDB == None:
                logger.debug('Fetching hash from ' + i + ' No previous known.')
            else:
                logger.debug('Fetching hash from ' + str(i) + ', ' + lastDB + ' last known')
            currentDB = self.performGet('getDBHash', i)
            if currentDB != False:
                logger.debug(i + " hash db (from request): " + currentDB)
            else:
                logger.warn("Error getting hash db status for " + i)
            if currentDB != False:
                if lastDB != currentDB:
                    logger.debug('Fetching hash from ' + i + ' - ' + currentDB + ' current hash.')
                    try:
                        blocks += self.performGet('getBlockHashes', i)
                    except TypeError:
                        logger.warn('Failed to get data hash from ' + i)
                        self.peerData[peer]['failCount'] -= 1
                if self._utils.validateHash(currentDB):
                    self._core.setAddressInfo(i, "DBHash", currentDB)
        if len(blocks.strip()) != 0:
            logger.debug('BLOCKS:' + blocks)
        blockList = blocks.split('\n')
        for i in blockList:
            if len(i.strip()) == 0:
                continue
            if self._utils.hasBlock(i):
                continue
            if i in self.ignoredHashes:
                continue
            #logger.debug('Exchanged block (blockList): ' + i)
            if not self._utils.validateHash(i):
                # skip hash if it isn't valid
                logger.warn('Hash ' + i + ' is not valid')
                continue
            else:
                self.newHashes[i] = 0
                logger.debug('Adding ' +  i + ' to hash database...')
                self._core.addToBlockDB(i)

        return

    def processBlocks(self):
        '''
            Work with the block database and download any missing blocks

            This is meant to be called from the communicator daemon on its timer.
        '''

        for i in self._core.getBlockList(unsaved=True).split("\n"):
            if i != "":
                if i in self.ignoredHashes:
                    continue
                try:
                    self.newHashes[i]
                except KeyError:
                    self.newHashes[i] = 0
                # check if a new hash has been around too long, delete it from database and add it to ignore list
                if self.newHashes[i] >= self.keepNewHash:
                    logger.warn('Ignoring block ' + i + ' because it took to long to get valid data.')
                    del self.newHashes[i]
                    self._core.removeBlock(i)
                    self.ignoredHashes.append(i)
                    continue
                self.newHashes[i] += 1
                logger.warn('UNSAVED BLOCK: ' + i)
                data = self.downloadBlock(i)
                if data:
                    del self.newHashes[i]
        return

    def downloadBlock(self, hash, peerTries=3):
        '''
            Download a block from random order of peers
        '''
        retVal = False
        peerList = self._core.listAdders()
        blocks = ''
        peerTryCount = 0
        for i in peerList:
            if self.peerData[i]['failCount'] >= self.highFailureAmount:
                continue
            if peerTryCount >= peerTries:
                break
            hasher = hashlib.sha3_256()
            data = self.performGet('getData', i, hash, skipHighFailureAddress=True)
            if data == False or len(data) > 10000000 or data == '':
                peerTryCount += 1
                continue
            try:
                data = base64.b64decode(data)
            except binascii.Error:
                data = b''
            hasher.update(data)
            digest = hasher.hexdigest()
            if type(digest) is bytes:
                digest = digest.decode()
            if digest == hash.strip():
                self._core.setData(data)
                logger.info('Successfully obtained data for ' + hash, timestamp=True)
                retVal = True
                if data.startswith(b'-txt-'):
                    self._core.setBlockType(hash, 'txt')
                    if len(data) < 120:
                        logger.debug('Block text:\n' + data.decode())
            else:
                logger.warn("Failed to validate " + hash + " " + " hash calculated was " + digest)
                peerTryCount += 1

        return retVal

    def urlencode(self, data):
        '''
            URL encodes the data
        '''
        return urllib.parse.quote_plus(data)

    def performGet(self, action, peer, data=None, skipHighFailureAddress=False, peerType='tor', selfCheck=True):
        '''
            Performs a request to a peer through Tor or i2p (currently only Tor)
        '''

        if not peer.endswith('.onion') and not peer.endswith('.onion/'):
            raise PeerError('Currently only Tor .onion peers are supported. You must manually specify .onion')
        
        if len(self._core.hsAdder.strip()) == 0:
            raise Exception("Could not perform self address check in performGet due to not knowing our address")
        if selfCheck:
            if peer.replace('/', '') == self._core.hsAdder:
                logger.warn('Tried to performget to own hidden service, but selfCheck was not set to false')
                return

        # Store peer in peerData dictionary (non permanent)
        if not peer in self.peerData:
            self.peerData[peer] = {'connectCount': 0, 'failCount': 0, 'lastConnectTime': math.floor(time.time())}
        socksPort = sys.argv[2]
        '''We use socks5h to use tor as DNS'''
        proxies = {'http': 'socks5://127.0.0.1:' + str(socksPort), 'https': 'socks5://127.0.0.1:' + str(socksPort)}
        headers = {'user-agent': 'PyOnionr'}
        url = 'http://' + peer + '/public/?action=' + self.urlencode(action)
        if data != None:
            url = url + '&data=' + self.urlencode(data)
        try:
            if skipHighFailureAddress and self.peerData[peer]['failCount'] > self.highFailureAmount:
                retData = False
                logger.debug('Skipping ' + peer + ' because of high failure rate')
            else:
                logger.debug('Contacting ' + peer + ' on port ' + socksPort)
                r = requests.get(url, headers=headers, proxies=proxies, timeout=(15, 30))
                retData = r.text
        except requests.exceptions.RequestException as e:
            logger.warn(action + " failed with peer " + peer + ": " + str(e))
            retData = False

        if not retData:
            self.peerData[peer]['failCount'] += 1
        else:
            self.peerData[peer]['connectCount'] += 1
            self.peerData[peer]['failCount'] -= 1
            self.peerData[peer]['lastConnectTime'] = math.floor(time.time())
        return retData


shouldRun = False
debug = True
developmentMode = False
if config.get('devmode', True):
    developmentMode = True
try:
    if sys.argv[1] == 'run':
        shouldRun = True
except IndexError:
    pass
if shouldRun:
    try:
        OnionrCommunicate(debug, developmentMode)
    except KeyboardInterrupt:
        sys.exit(1)
        pass
