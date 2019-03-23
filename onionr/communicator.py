#!/usr/bin/env python3
'''
    Onionr - P2P Anonymous Storage Network

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
import sys, os, core, config, json, requests, time, logger, threading, base64, onionr, uuid, binascii
from dependencies import secrets
from utils import networkmerger
import onionrexceptions, onionrpeers, onionrevents as events, onionrplugins as plugins, onionrblockapi as block
from communicatorutils import onionrdaemontools
from communicatorutils import servicecreator
import onionrservices, onionr, onionrproofs
from communicatorutils import onionrcommunicatortimers, proxypicker

OnionrCommunicatorTimers = onionrcommunicatortimers.OnionrCommunicatorTimers

config.reload()
class OnionrCommunicatorDaemon:
    def __init__(self, onionrInst, proxyPort, developmentMode=config.get('general.dev_mode', False)):
        onionrInst.communicatorInst = self
        # configure logger and stuff
        onionr.Onionr.setupConfig('data/', self = self)
        self.proxyPort = proxyPort

        self.isOnline = True # Assume we're connected to the internet

        # list of timer instances
        self.timers = []

        # initialize core with Tor socks port being 3rd argument
        self.proxyPort = proxyPort
        self._core = onionrInst.onionrCore

        self.blocksToUpload = []

        # loop time.sleep delay in seconds
        self.delay = 1

        # lists of connected peers and peers we know we can't reach currently
        self.onlinePeers = []
        self.offlinePeers = []
        self.cooldownPeer = {}
        self.connectTimes = {}
        self.peerProfiles = [] # list of peer's profiles (onionrpeers.PeerProfile instances)
        self.newPeers = [] # Peers merged to us. Don't add to db until we know they're reachable

        # amount of threads running by name, used to prevent too many
        self.threadCounts = {}

        # set true when shutdown command received
        self.shutdown = False

        # list of new blocks to download, added to when new block lists are fetched from peers
        self.blockQueue = {}

        # list of blocks currently downloading, avoid s
        self.currentDownloading = []

        # timestamp when the last online node was seen
        self.lastNodeSeen = None

        # Dict of time stamps for peer's block list lookup times, to avoid downloading full lists all the time
        self.dbTimestamps = {}

        # Clear the daemon queue for any dead messages
        if os.path.exists(self._core.queueDB):
            self._core.clearDaemonQueue()

        # Loads in and starts the enabled plugins
        plugins.reload()

        # daemon tools are misc daemon functions, e.g. announce to online peers
        # intended only for use by OnionrCommunicatorDaemon
        self.daemonTools = onionrdaemontools.DaemonTools(self)

        # time app started running for info/statistics purposes
        self.startTime = self._core._utils.getEpoch()

        if developmentMode:
            OnionrCommunicatorTimers(self, self.heartbeat, 30)

        # Set timers, function reference, seconds
        # requiresPeer True means the timer function won't fire if we have no connected peers
        peerPoolTimer = OnionrCommunicatorTimers(self, self.getOnlinePeers, 60, maxThreads=1)
        OnionrCommunicatorTimers(self, self.runCheck, 2, maxThreads=1)
        OnionrCommunicatorTimers(self, self.lookupBlocks, self._core.config.get('timers.lookupBlocks'), requiresPeer=True, maxThreads=1)
        OnionrCommunicatorTimers(self, self.getBlocks, self._core.config.get('timers.getBlocks'), requiresPeer=True, maxThreads=2)
        OnionrCommunicatorTimers(self, self.clearOfflinePeer, 58)
        blockCleanupTimer = OnionrCommunicatorTimers(self, self.daemonTools.cleanOldBlocks, 65)
        OnionrCommunicatorTimers(self, self.lookupAdders, 60, requiresPeer=True)
        OnionrCommunicatorTimers(self, self.daemonTools.cooldownPeer, 30, requiresPeer=True)
        OnionrCommunicatorTimers(self, self.uploadBlock, 10, requiresPeer=True, maxThreads=1)
        OnionrCommunicatorTimers(self, self.daemonCommands, 6, maxThreads=1)
        OnionrCommunicatorTimers(self, self.detectAPICrash, 30, maxThreads=1)
        OnionrCommunicatorTimers(self, servicecreator.service_creator, 5, maxThreads=10, myArgs=(self,))
        deniableBlockTimer = OnionrCommunicatorTimers(self, self.daemonTools.insertDeniableBlock, 180, requiresPeer=True, maxThreads=1)

        netCheckTimer = OnionrCommunicatorTimers(self, self.daemonTools.netCheck, 600)
        if config.get('general.security_level') == 0:
            announceTimer = OnionrCommunicatorTimers(self, self.daemonTools.announceNode, 3600, requiresPeer=True, maxThreads=1)
            announceTimer.count = (announceTimer.frequency - 120)
        else:
            logger.debug('Will not announce node.')
        cleanupTimer = OnionrCommunicatorTimers(self, self.peerCleanup, 300, requiresPeer=True)
        forwardSecrecyTimer = OnionrCommunicatorTimers(self, self.daemonTools.cleanKeys, 15, maxThreads=1)

        # set loop to execute instantly to load up peer pool (replaced old pool init wait)
        peerPoolTimer.count = (peerPoolTimer.frequency - 1)
        cleanupTimer.count = (cleanupTimer.frequency - 60)
        deniableBlockTimer.count = (deniableBlockTimer.frequency - 175)
        blockCleanupTimer.count = (blockCleanupTimer.frequency - 5)
        #forwardSecrecyTimer.count = (forwardSecrecyTimer.frequency - 990)

        if config.get('general.socket_servers'):
            self.services = onionrservices.OnionrServices(self._core)
        else:
            self.services = None

        # Main daemon loop, mainly for calling timers, don't do any complex operations here to avoid locking
        try:
            while not self.shutdown:
                for i in self.timers:
                    if self.shutdown:
                        break
                    i.processTimer()
                time.sleep(self.delay)
                # Debug to print out used FDs (regular and net)
                #proc = psutil.Process()
                #print(proc.open_files(), len(psutil.net_connections()))
        except KeyboardInterrupt:
            self.shutdown = True
            pass

        logger.info('Goodbye.')
        self._core.killSockets = True
        self._core._utils.localCommand('shutdown') # shutdown the api
        time.sleep(0.5)

    def lookupAdders(self):
        '''Lookup new peer addresses'''
        logger.info('Looking up new addresses...')
        tryAmount = 1
        newPeers = []
        for i in range(tryAmount):
            # Download new peer address list from random online peers
            if len(newPeers) > 10000:
                # Dont get new peers if we have too many queued up
                break
            peer = self.pickOnlinePeer()
            newAdders = self.peerAction(peer, action='pex')
            try:
                newPeers = newAdders.split(',')
            except AttributeError:
                pass
        else:
            # Validate new peers are good format and not already in queue
            invalid = []
            for x in newPeers:
                x = x.strip()
                if not self._core._utils.validateID(x) or x in self.newPeers or x == self._core.hsAddress:
                    invalid.append(x)
            for x in invalid:
                newPeers.remove(x)
            self.newPeers.extend(newPeers)
        self.decrementThreadCount('lookupAdders')

    def lookupBlocks(self):
        '''Lookup new blocks & add them to download queue'''
        logger.info('Looking up new blocks...')
        tryAmount = 2
        newBlocks = ''
        existingBlocks = self._core.getBlockList()
        triedPeers = [] # list of peers we've tried this time around
        maxBacklog = 1560 # Max amount of *new* block hashes to have already in queue, to avoid memory exhaustion
        lastLookupTime = 0 # Last time we looked up a particular peer's list
        for i in range(tryAmount):
            listLookupCommand = 'getblocklist' # This is defined here to reset it each time
            if len(self.blockQueue) >= maxBacklog:
                break
            if not self.isOnline:
                break
            # check if disk allocation is used
            if self._core._utils.storageCounter.isFull():
                logger.debug('Not looking up new blocks due to maximum amount of allowed disk space used')
                break
            peer = self.pickOnlinePeer() # select random online peer
            # if we've already tried all the online peers this time around, stop
            if peer in triedPeers:
                if len(self.onlinePeers) == len(triedPeers):
                    break
                else:
                    continue
            triedPeers.append(peer)

            # Get the last time we looked up a peer's stamp to only fetch blocks since then.
            # Saved in memory only for privacy reasons
            try:
                lastLookupTime = self.dbTimestamps[peer]
            except KeyError:
                lastLookupTime = 0
            else:
                listLookupCommand += '?date=%s' % (lastLookupTime,)
            try:
                newBlocks = self.peerAction(peer, listLookupCommand) # get list of new block hashes
            except Exception as error:
                logger.warn('Could not get new blocks from %s.' % peer, error = error)
                newBlocks = False
            else:
                self.dbTimestamps[peer] = self._core._utils.getRoundedEpoch(roundS=60)
            if newBlocks != False:
                # if request was a success
                for i in newBlocks.split('\n'):
                    if self._core._utils.validateHash(i):
                        # if newline seperated string is valid hash
                        if not i in existingBlocks:
                            # if block does not exist on disk and is not already in block queue
                            if i not in self.blockQueue:
                                if onionrproofs.hashMeetsDifficulty(i) and not self._core._blacklist.inBlacklist(i):
                                    if len(self.blockQueue) <= 1000000:
                                        self.blockQueue[i] = [peer] # add blocks to download queue
                            else:
                                if peer not in self.blockQueue[i]:
                                    if len(self.blockQueue[i]) < 10:
                                        self.blockQueue[i].append(peer)
        self.decrementThreadCount('lookupBlocks')
        return

    def getBlocks(self):
        '''download new blocks in queue'''
        for blockHash in list(self.blockQueue):
            triedQueuePeers = [] # List of peers we've tried for a block
            try:
                blockPeers = list(self.blockQueue[blockHash])
            except KeyError:
                blockPeers = []
            removeFromQueue = True
            if self.shutdown or not self.isOnline:
                # Exit loop if shutting down or offline
                break
            # Do not download blocks being downloaded or that are already saved (edge cases)
            if blockHash in self.currentDownloading:
                #logger.debug('Already downloading block %s...' % blockHash)
                continue
            if blockHash in self._core.getBlockList():
                #logger.debug('Block %s is already saved.' % (blockHash,))
                try:
                    del self.blockQueue[blockHash]
                except KeyError:
                    pass
                continue
            if self._core._blacklist.inBlacklist(blockHash):
                continue
            if self._core._utils.storageCounter.isFull():
                break
            self.currentDownloading.append(blockHash) # So we can avoid concurrent downloading in other threads of same block
            if len(blockPeers) == 0:
                peerUsed = self.pickOnlinePeer()
            else:
                blockPeers = self._core._crypto.randomShuffle(blockPeers)
                peerUsed = blockPeers.pop(0)

            if not self.shutdown and peerUsed.strip() != '':
                logger.info("Attempting to download %s from %s..." % (blockHash[:12], peerUsed))
            content = self.peerAction(peerUsed, 'getdata/' + blockHash) # block content from random peer (includes metadata)
            if content != False and len(content) > 0:
                try:
                    content = content.encode()
                except AttributeError:
                    pass

                realHash = self._core._crypto.sha3Hash(content)
                try:
                    realHash = realHash.decode() # bytes on some versions for some reason
                except AttributeError:
                    pass
                if realHash == blockHash:
                    content = content.decode() # decode here because sha3Hash needs bytes above
                    metas = self._core._utils.getBlockMetadataFromData(content) # returns tuple(metadata, meta), meta is also in metadata
                    metadata = metas[0]
                    if self._core._utils.validateMetadata(metadata, metas[2]): # check if metadata is valid, and verify nonce
                        if self._core._crypto.verifyPow(content): # check if POW is enough/correct
                            logger.info('Attempting to save block %s...' % blockHash[:12])
                            try:
                                self._core.setData(content)
                            except onionrexceptions.DiskAllocationReached:
                                logger.error('Reached disk allocation allowance, cannot save block %s.' % blockHash)
                                removeFromQueue = False
                            else:
                                self._core.addToBlockDB(blockHash, dataSaved=True)
                                self._core._utils.processBlockMetadata(blockHash) # caches block metadata values to block database
                        else:
                            logger.warn('POW failed for block %s.' % blockHash)
                    else:
                        if self._core._blacklist.inBlacklist(realHash):
                            logger.warn('Block %s is blacklisted.' % (realHash,))
                        else:
                            logger.warn('Metadata for block %s is invalid.' % blockHash)
                            self._core._blacklist.addToDB(blockHash)
                else:
                    # if block didn't meet expected hash
                    tempHash = self._core._crypto.sha3Hash(content) # lazy hack, TODO use var
                    try:
                        tempHash = tempHash.decode()
                    except AttributeError:
                        pass
                    # Punish peer for sharing invalid block (not always malicious, but is bad regardless)
                    onionrpeers.PeerProfiles(peerUsed, self._core).addScore(-50)
                    if tempHash != 'ed55e34cb828232d6c14da0479709bfa10a0923dca2b380496e6b2ed4f7a0253':
                        # Dumb hack for 404 response from peer. Don't log it if 404 since its likely not malicious or a critical error.
                        logger.warn('Block hash validation failed for ' + blockHash + ' got ' + tempHash)
                    else:
                        removeFromQueue = False # Don't remove from queue if 404
                if removeFromQueue:
                    try:
                        del self.blockQueue[blockHash] # remove from block queue both if success or false
                    except KeyError:
                        pass
            self.currentDownloading.remove(blockHash)
        self.decrementThreadCount('getBlocks')
        return

    def pickOnlinePeer(self):
        '''randomly picks peer from pool without bias (using secrets module)'''
        retData = ''
        while True:
            peerLength = len(self.onlinePeers)
            if peerLength <= 0:
                break
            try:
                # get a random online peer, securely. May get stuck in loop if network is lost or if all peers in pool magically disconnect at once
                retData = self.onlinePeers[self._core._crypto.secrets.randbelow(peerLength)]
            except IndexError:
                pass
            else:
                break
        return retData

    def decrementThreadCount(self, threadName):
        '''Decrement amount of a thread name if more than zero, called when a function meant to be run in a thread ends'''
        try:
            if self.threadCounts[threadName] > 0:
                self.threadCounts[threadName] -= 1
        except KeyError:
            pass

    def clearOfflinePeer(self):
        '''Removes the longest offline peer to retry later'''
        try:
            removed = self.offlinePeers.pop(0)
        except IndexError:
            pass
        else:
            logger.debug('Removed ' + removed + ' from offline list, will try them again.')
        self.decrementThreadCount('clearOfflinePeer')

    def getOnlinePeers(self):
        '''
            Manages the self.onlinePeers attribute list, connects to more peers if we have none connected
        '''

        logger.debug('Refreshing peer pool...')
        maxPeers = int(config.get('peers.max_connect', 10))
        needed = maxPeers - len(self.onlinePeers)

        for i in range(needed):
            if len(self.onlinePeers) == 0:
                self.connectNewPeer(useBootstrap=True)
            else:
                self.connectNewPeer()

            if self.shutdown:
                break
        else:
            if len(self.onlinePeers) == 0:
                logger.debug('Couldn\'t connect to any peers.' + (' Last node seen %s ago.' % self.daemonTools.humanReadableTime(time.time() - self.lastNodeSeen) if not self.lastNodeSeen is None else ''))
            else:
                self.lastNodeSeen = time.time()
        self.decrementThreadCount('getOnlinePeers')

    def addBootstrapListToPeerList(self, peerList):
        '''
            Add the bootstrap list to the peer list (no duplicates)
        '''
        for i in self._core.bootstrapList:
            if i not in peerList and i not in self.offlinePeers and i != self._core.hsAddress and len(str(i).strip()) > 0:
                peerList.append(i)
                self._core.addAddress(i)

    def connectNewPeer(self, peer='', useBootstrap=False):
        '''Adds a new random online peer to self.onlinePeers'''
        retData = False
        tried = self.offlinePeers
        if peer != '':
            if self._core._utils.validateID(peer):
                peerList = [peer]
            else:
                raise onionrexceptions.InvalidAddress('Will not attempt connection test to invalid address')
        else:
            peerList = self._core.listAdders()

        mainPeerList = self._core.listAdders()
        peerList = onionrpeers.getScoreSortedPeerList(self._core)

        if len(peerList) < 8 or secrets.randbelow(4) == 3:
            tryingNew = []
            for x in self.newPeers:
                if x not in peerList:
                    peerList.append(x)
                    tryingNew.append(x)
            for i in tryingNew:
                self.newPeers.remove(i)
        
        if len(peerList) == 0 or useBootstrap:
            # Avoid duplicating bootstrap addresses in peerList
            self.addBootstrapListToPeerList(peerList)

        for address in peerList:
            if not config.get('tor.v3onions') and len(address) == 62:
                continue
            if address == self._core.hsAddress:
                continue
            if len(address) == 0 or address in tried or address in self.onlinePeers or address in self.cooldownPeer:
                continue
            if self.shutdown:
                return
            if self.peerAction(address, 'ping') == 'pong!':
                time.sleep(0.1)
                if address not in mainPeerList:
                    networkmerger.mergeAdders(address, self._core)
                if address not in self.onlinePeers:
                    logger.info('Connected to ' + address)
                    self.onlinePeers.append(address)
                    self.connectTimes[address] = self._core._utils.getEpoch()
                retData = address

                # add peer to profile list if they're not in it
                for profile in self.peerProfiles:
                    if profile.address == address:
                        break
                else:
                    self.peerProfiles.append(onionrpeers.PeerProfiles(address, self._core))
                break
            else:
                tried.append(address)
                logger.debug('Failed to connect to ' + address)
        return retData

    def removeOnlinePeer(self, peer):
        '''Remove an online peer'''
        try:
            del self.connectTimes[peer]
        except KeyError:
            pass
        try:
            del self.dbTimestamps[peer]
        except KeyError:
            pass
        try:
            self.onlinePeers.remove(peer)
        except ValueError:
            pass

    def peerCleanup(self):
        '''This just calls onionrpeers.cleanupPeers, which removes dead or bad peers (offline too long, too slow)'''
        onionrpeers.peerCleanup(self._core)
        self.decrementThreadCount('peerCleanup')

    def printOnlinePeers(self):
        '''logs online peer list'''
        if len(self.onlinePeers) == 0:
            logger.warn('No online peers')
        else:
            logger.info('Online peers:')
            for i in self.onlinePeers:
                score = str(self.getPeerProfileInstance(i).score)
                logger.info(i + ', score: ' + score)

    def peerAction(self, peer, action, data='', returnHeaders=False):
        '''Perform a get request to a peer'''
        if len(peer) == 0:
            return False
        #logger.debug('Performing ' + action + ' with ' + peer + ' on port ' + str(self.proxyPort))
        url = 'http://%s/%s' % (peer, action)
        if len(data) > 0:
            url += '&data=' + data

        self._core.setAddressInfo(peer, 'lastConnectAttempt', self._core._utils.getEpoch()) # mark the time we're trying to request this peer

        retData = self._core._utils.doGetRequest(url, port=self.proxyPort)
        # if request failed, (error), mark peer offline
        if retData == False:
            try:
                self.getPeerProfileInstance(peer).addScore(-10)
                self.removeOnlinePeer(peer)
                if action != 'ping':
                    self.getOnlinePeers() # Will only add a new peer to pool if needed
            except ValueError:
                pass
        else:
            self._core.setAddressInfo(peer, 'lastConnect', self._core._utils.getEpoch())
            self.getPeerProfileInstance(peer).addScore(1)
        return retData # If returnHeaders, returns tuple of data, headers. if not, just data string

    def getPeerProfileInstance(self, peer):
        '''Gets a peer profile instance from the list of profiles, by address name'''
        for i in self.peerProfiles:
            # if the peer's profile is already loaded, return that
            if i.address == peer:
                retData = i
                break
        else:
            # if the peer's profile is not loaded, return a new one. connectNewPeer adds it the list on connect
            retData = onionrpeers.PeerProfiles(peer, self._core)
        return retData

    def getUptime(self):
        return self._core._utils.getEpoch() - self.startTime

    def heartbeat(self):
        '''Show a heartbeat debug message'''
        logger.debug('Heartbeat. Node running for %s.' % self.daemonTools.humanReadableTime(self.getUptime()))
        self.decrementThreadCount('heartbeat')

    def daemonCommands(self):
        '''
            Process daemon commands from daemonQueue
        '''
        cmd = self._core.daemonQueue()
        response = ''
        if cmd is not False:
            events.event('daemon_command', onionr = None, data = {'cmd' : cmd})
            if cmd[0] == 'shutdown':
                self.shutdown = True
            elif cmd[0] == 'announceNode':
                if len(self.onlinePeers) > 0:
                    self.announce(cmd[1])
                else:
                    logger.debug("No nodes connected. Will not introduce node.")
            elif cmd[0] == 'runCheck': # deprecated
                logger.debug('Status check; looks good.')
                open(self._core.dataDir + '.runcheck', 'w+').close()
            elif cmd[0] == 'connectedPeers':
                response = '\n'.join(list(self.onlinePeers)).strip()
                if response == '':
                    response = 'none'
            elif cmd[0] == 'localCommand':
                response = self._core._utils.localCommand(cmd[1])
            elif cmd[0] == 'pex':
                for i in self.timers:
                    if i.timerFunction.__name__ == 'lookupAdders':
                        i.count = (i.frequency - 1)
            elif cmd[0] == 'uploadBlock':
                self.blocksToUpload.append(cmd[1])

            if cmd[0] not in ('', None):
                if response != '':
                    self._core._utils.localCommand('queueResponseAdd/' + cmd[4], post=True, postData={'data': response})
            response = ''

        self.decrementThreadCount('daemonCommands')

    def uploadBlock(self):
        '''Upload our block to a few peers'''
        # when inserting a block, we try to upload it to a few peers to add some deniability
        triedPeers = []
        finishedUploads = []
        self.blocksToUpload = self._core._crypto.randomShuffle(self.blocksToUpload)
        if len(self.blocksToUpload) != 0:
            for bl in self.blocksToUpload:
                if not self._core._utils.validateHash(bl):
                    logger.warn('Requested to upload invalid block')
                    self.decrementThreadCount('uploadBlock')
                    return
                for i in range(min(len(self.onlinePeers), 6)):
                    peer = self.pickOnlinePeer()
                    if peer in triedPeers:
                        continue
                    triedPeers.append(peer)
                    url = 'http://' + peer + '/upload'
                    data = {'block': block.Block(bl).getRaw()}
                    proxyType = proxypicker.pick_proxy(peer)
                    logger.info("Uploading block to " + peer)
                    if not self._core._utils.doPostRequest(url, data=data, proxyType=proxyType) == False:
                        self._core._utils.localCommand('waitforshare/' + bl, post=True)
                        finishedUploads.append(bl)
        for x in finishedUploads:
            try:
                self.blocksToUpload.remove(x)
            except ValueError:
                pass
        self.decrementThreadCount('uploadBlock')

    def announce(self, peer):
        '''Announce to peers our address'''
        if self.daemonTools.announceNode() == False:
            logger.warn('Could not introduce node.')

    def detectAPICrash(self):
        '''exit if the api server crashes/stops'''
        if self._core._utils.localCommand('ping', silent=False) not in ('pong', 'pong!'):
            for i in range(8):
                if self._core._utils.localCommand('ping') in ('pong', 'pong!') or self.shutdown:
                    break # break for loop
                time.sleep(1)
            else:
                # This executes if the api is NOT detected to be running
                events.event('daemon_crash', onionr = None, data = {})
                logger.error('Daemon detected API crash (or otherwise unable to reach API after long time), stopping...')
                self.shutdown = True
        self.decrementThreadCount('detectAPICrash')

    def runCheck(self):
        if self.daemonTools.runCheck():
            logger.debug('Status check; looks good.')

        self.decrementThreadCount('runCheck')

def startCommunicator(onionrInst, proxyPort):
    OnionrCommunicatorDaemon(onionrInst, proxyPort)