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
import onionrexceptions, onionrpeers, onionrevents as events, onionrplugins as plugins, onionrblockapi as block
from communicatorutils import onionrdaemontools, servicecreator, onionrcommunicatortimers
from communicatorutils import proxypicker, downloadblocks, lookupblocks, lookupadders
from communicatorutils import servicecreator, connectnewpeers, uploadblocks
from communicatorutils import daemonqueuehandler
import onionrservices, onionr, onionrproofs

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

        # Timers to periodically lookup new blocks and download them
        OnionrCommunicatorTimers(self, self.lookupBlocks, self._core.config.get('timers.lookupBlocks'), requiresPeer=True, maxThreads=1)
        OnionrCommunicatorTimers(self, self.getBlocks, self._core.config.get('timers.getBlocks'), requiresPeer=True, maxThreads=2)

        # Timer to reset the longest offline peer so contact can be attempted again
        OnionrCommunicatorTimers(self, self.clearOfflinePeer, 58)

        # Timer to cleanup old blocks
        blockCleanupTimer = OnionrCommunicatorTimers(self, self.daemonTools.cleanOldBlocks, 65)

        # Timer to discover new peers
        OnionrCommunicatorTimers(self, self.lookupAdders, 60, requiresPeer=True)

        # Timer for adjusting which peers we actively communicate to at any given time, to avoid over-using peers
        OnionrCommunicatorTimers(self, self.daemonTools.cooldownPeer, 30, requiresPeer=True)

        # Timer to read the upload queue and upload the entries to peers
        OnionrCommunicatorTimers(self, self.uploadBlock, 10, requiresPeer=True, maxThreads=1)

        # Timer to process the daemon command queue
        OnionrCommunicatorTimers(self, self.daemonCommands, 6, maxThreads=1)

        # Timer that kills Onionr if the API server crashes
        OnionrCommunicatorTimers(self, self.detectAPICrash, 30, maxThreads=1)

        # Setup direct connections
        if config.get('general.socket_servers', False):
            self.services = onionrservices.OnionrServices(self._core)
            self.active_services = []
            self.service_greenlets = []
            OnionrCommunicatorTimers(self, servicecreator.service_creator, 5, maxThreads=50, myArgs=(self,))
        else:
            self.services = None
        
        # This timer creates deniable blocks, in an attempt to further obfuscate block insertion metadata
        deniableBlockTimer = OnionrCommunicatorTimers(self, self.daemonTools.insertDeniableBlock, 180, requiresPeer=True, maxThreads=1)

        # Timer to check for connectivity, through Tor to various high-profile onion services
        netCheckTimer = OnionrCommunicatorTimers(self, self.daemonTools.netCheck, 600)

        # Announce the public API server transport address to other nodes if security level allows
        if config.get('general.security_level', 1) == 0:
            # Default to high security level incase config breaks
            announceTimer = OnionrCommunicatorTimers(self, self.daemonTools.announceNode, 3600, requiresPeer=True, maxThreads=1)
            announceTimer.count = (announceTimer.frequency - 120)
        else:
            logger.debug('Will not announce node.')
        
        # Timer to delete malfunctioning or long-dead peers
        cleanupTimer = OnionrCommunicatorTimers(self, self.peerCleanup, 300, requiresPeer=True)

        # Timer to cleanup dead ephemeral forward secrecy keys 
        forwardSecrecyTimer = OnionrCommunicatorTimers(self, self.daemonTools.cleanKeys, 15, maxThreads=1)

        # Adjust initial timer triggers
        peerPoolTimer.count = (peerPoolTimer.frequency - 1)
        cleanupTimer.count = (cleanupTimer.frequency - 60)
        deniableBlockTimer.count = (deniableBlockTimer.frequency - 175)
        blockCleanupTimer.count = (blockCleanupTimer.frequency - 5)

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

        logger.info('Goodbye. (Onionr is cleaning up, and will exit)')
        try:
            self.service_greenlets
        except AttributeError:
            pass
        else:
            for server in self.service_greenlets:
                server.stop()
        self._core._utils.localCommand('shutdown') # shutdown the api
        time.sleep(0.5)

    def lookupAdders(self):
        '''Lookup new peer addresses'''
        lookupadders.lookup_new_peer_transports_with_communicator(self)

    def lookupBlocks(self):
        '''Lookup new blocks & add them to download queue'''
        lookupblocks.lookup_blocks_from_communicator(self)

    def getBlocks(self):
        '''download new blocks in queue'''
        downloadblocks.download_blocks_from_communicator(self)

    def decrementThreadCount(self, threadName):
        '''Decrement amount of a thread name if more than zero, called when a function meant to be run in a thread ends'''
        try:
            if self.threadCounts[threadName] > 0:
                self.threadCounts[threadName] -= 1
        except KeyError:
            pass

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
        connectnewpeers.connect_new_peer_to_communicator(self, peer, useBootstrap)

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
        daemonqueuehandler.handle_daemon_commands(self)

    def uploadBlock(self):
        '''Upload our block to a few peers'''
        uploadblocks.upload_blocks_from_communicator(self)

    def announce(self, peer):
        '''Announce to peers our address'''
        if self.daemonTools.announceNode() == False:
            logger.warn('Could not introduce node.')

    def detectAPICrash(self):
        '''exit if the api server crashes/stops'''
        if self._core._utils.localCommand('ping', silent=False) not in ('pong', 'pong!'):
            for i in range(20):
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