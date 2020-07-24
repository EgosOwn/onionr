"""Onionr - Private P2P Communication.

This file contains both the OnionrCommunicate class for
communcating with peers and code to operate as a daemon,
getting commands from the command queue database
"""
import time

import config
import logger
import onionrpeers
import onionrplugins as plugins
from . import onlinepeers, uploadqueue
from communicatorutils import servicecreator
from communicatorutils import onionrcommunicatortimers
from communicatorutils import downloadblocks
from communicatorutils import lookupblocks
from communicatorutils import lookupadders
from communicatorutils import connectnewpeers
from communicatorutils import uploadblocks
from communicatorutils import announcenode, deniableinserts
from communicatorutils import cooldownpeer
from communicatorutils import housekeeping
from communicatorutils import netcheck
from onionrutils import epoch
from onionrcommands.openwebinterface import get_url
from etc import humanreadabletime
import onionrservices
from netcontroller import NetController
from . import bootstrappeers
from . import daemoneventhooks
"""
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
"""

OnionrCommunicatorTimers = onionrcommunicatortimers.OnionrCommunicatorTimers

config.reload()


class OnionrCommunicatorDaemon:
    def __init__(self, shared_state, developmentMode=None):
        if developmentMode is None:
            developmentMode = config.get('general.dev_mode', False)

        # configure logger and stuff
        self.config = config
        self.isOnline = True  # Assume we're connected to the internet
        self.shared_state = shared_state  # TooManyObjects module

        if config.get('general.offline_mode', False):
            self.isOnline = False

        # list of timer instances
        self.timers = []

        # initialize core with Tor socks port being 3rd argument
        self.proxyPort = shared_state.get(NetController).socksPort

        # Upload information, list of blocks to upload
        self.blocksToUpload = []
        self.upload_session_manager = self.shared_state.get(
            uploadblocks.sessionmanager.BlockUploadSessionManager)
        self.shared_state.share_object()

        # loop time.sleep delay in seconds
        self.delay = 1

        # lists of connected peers and peers we know we can't reach currently
        self.onlinePeers = []
        self.offlinePeers = []
        self.cooldownPeer = {}
        self.connectTimes = {}
        # list of peer's profiles (onionrpeers.PeerProfile instances)
        self.peerProfiles = []
        # Peers merged to us. Don't add to db until we know they're reachable
        self.newPeers = []
        self.announceProgress = {}
        self.announceCache = {}

        self.generating_blocks = []

        # amount of threads running by name, used to prevent too many
        self.threadCounts = {}

        # set true when shutdown command received
        self.shutdown = False

        # list of new blocks to download
        # added to when new block lists are fetched from peers
        self.blockQueue = {}

        # list of blocks currently downloading, avoid s
        self.currentDownloading = []

        # timestamp when the last online node was seen
        self.lastNodeSeen = None

        # Dict of time stamps for peer's block list lookup times,
        # to avoid downloading full lists all the time
        self.dbTimestamps = {}

        # Loads in and starts the enabled plugins
        plugins.reload()

        # time app started running for info/statistics purposes
        self.startTime = epoch.get_epoch()

        # extends our upload list and saves our list when Onionr exits
        uploadqueue.UploadQueue(self)

        if developmentMode:
            OnionrCommunicatorTimers(self, self.heartbeat, 30)

        # Set timers, function reference, seconds
        # requires_peer True means the timer function won't fire if we
        # have no connected peers
        peerPoolTimer = OnionrCommunicatorTimers(
            self, onlinepeers.get_online_peers, 60, max_threads=1,
            my_args=[self])

        # Timers to periodically lookup new blocks and download them
        lookup_blocks_timer = OnionrCommunicatorTimers(
            self,
            lookupblocks.lookup_blocks_from_communicator,
            config.get('timers.lookupBlocks', 25),
            my_args=[self], requires_peer=True, max_threads=1)

        """The block download timer is accessed by the block lookup function
        to trigger faster download starts"""
        self.download_blocks_timer = OnionrCommunicatorTimers(
            self, self.getBlocks, config.get('timers.getBlocks', 10),
            requires_peer=True, max_threads=5)

        # Timer to reset the longest offline peer
        # so contact can be attempted again
        OnionrCommunicatorTimers(
            self, onlinepeers.clear_offline_peer, 58, my_args=[self],
            max_threads=1)

        # Timer to cleanup old blocks
        blockCleanupTimer = OnionrCommunicatorTimers(
            self, housekeeping.clean_old_blocks, 20, my_args=[self],
            max_threads=1)

        # Timer to discover new peers
        OnionrCommunicatorTimers(
            self, lookupadders.lookup_new_peer_transports_with_communicator,
            60, requires_peer=True, my_args=[self], max_threads=2)

        # Timer for adjusting which peers
        # we actively communicate to at any given time,
        # to avoid over-using peers
        OnionrCommunicatorTimers(
            self, cooldownpeer.cooldown_peer, 30,
            my_args=[self], requires_peer=True)

        # Timer to read the upload queue and upload the entries to peers
        OnionrCommunicatorTimers(
            self, uploadblocks.upload_blocks_from_communicator,
            5, my_args=[self], requires_peer=True, max_threads=1)

        # Setup direct connections
        if config.get('general.ephemeral_tunnels', False):
            self.services = onionrservices.OnionrServices()
            self.active_services = []
            self.service_greenlets = []
            OnionrCommunicatorTimers(
                self, servicecreator.service_creator, 5,
                max_threads=50, my_args=[self])
        else:
            self.services = None

        # {peer_pubkey: ephemeral_address}, the address to reach them
        self.direct_connection_clients = {}

        # This timer creates deniable blocks,
        # in an attempt to further obfuscate block insertion metadata
        if config.get('general.insert_deniable_blocks', True):
            deniableBlockTimer = OnionrCommunicatorTimers(
                self, deniableinserts.insert_deniable_block,
                180, my_args=[self], requires_peer=True, max_threads=1)
            deniableBlockTimer.count = (deniableBlockTimer.frequency - 175)

        # Timer to check for connectivity,
        # through Tor to various high-profile onion services
        OnionrCommunicatorTimers(self, netcheck.net_check, 500,
                                 my_args=[self], max_threads=1)

        # Announce the public API server transport address
        # to other nodes if security level allows
        if config.get('general.security_level', 1) == 0 \
                and config.get('general.announce_node', True):
            # Default to high security level incase config breaks
            announceTimer = OnionrCommunicatorTimers(
                self,
                announcenode.announce_node,
                3600, my_args=[self], requires_peer=True, max_threads=1)
            announceTimer.count = (announceTimer.frequency - 60)
        else:
            logger.debug('Will not announce node.')

        # Timer to delete malfunctioning or long-dead peers
        cleanupTimer = OnionrCommunicatorTimers(
            self, self.peerCleanup, 300, requires_peer=True)

        # Timer to cleanup dead ephemeral forward secrecy keys
        OnionrCommunicatorTimers(
            self, housekeeping.clean_keys, 15, my_args=[self], max_threads=1)

        # Adjust initial timer triggers
        peerPoolTimer.count = (peerPoolTimer.frequency - 1)
        cleanupTimer.count = (cleanupTimer.frequency - 60)
        blockCleanupTimer.count = (blockCleanupTimer.frequency - 2)
        lookup_blocks_timer = (lookup_blocks_timer.frequency - 2)

        shared_state.add(self)

        if config.get('general.use_bootstrap_list', True):
            bootstrappeers.add_bootstrap_list_to_peer_list(
                self, [], db_only=True)

        daemoneventhooks.daemon_event_handlers(shared_state)

        if not config.get('onboarding.done', True):
            logger.info(
                'First run detected. Run openhome to get setup.',
                terminal=True)
            get_url()

            while not config.get('onboarding.done', True) and \
                    not self.shutdown:
                try:
                    time.sleep(2)
                except KeyboardInterrupt:
                    self.shutdown = True

        # Main daemon loop, mainly for calling timers,
        # don't do any complex operations here to avoid locking
        try:
            while not self.shutdown:
                for i in self.timers:
                    if self.shutdown:
                        break
                    i.processTimer()
                time.sleep(self.delay)
        except KeyboardInterrupt:
            self.shutdown = True

        logger.info(
            'Goodbye. (Onionr is cleaning up, and will exit)', terminal=True)
        try:
            self.service_greenlets
        except AttributeError:
            pass
        else:
            # Stop onionr direct connection services
            for server in self.service_greenlets:
                server.stop()
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            pass

    def getBlocks(self):
        """Download new blocks in queue."""
        downloadblocks.download_blocks_from_communicator(self)

    def decrementThreadCount(self, threadName):
        """Decrement amount of a thread name if more than zero.

        called when a function meant to be run in a thread ends
        """
        try:
            if self.threadCounts[threadName] > 0:
                self.threadCounts[threadName] -= 1
        except KeyError:
            pass

    def connectNewPeer(self, peer='', useBootstrap=False):
        """Adds a new random online peer to self.onlinePeers"""
        connectnewpeers.connect_new_peer_to_communicator(
            self, peer, useBootstrap)

    def peerCleanup(self):
        """This just calls onionrpeers.cleanupPeers.

        Remove dead or bad peers (offline too long, too slow)"""
        onionrpeers.peer_cleanup()
        self.decrementThreadCount('peerCleanup')

    def getPeerProfileInstance(self, peer):
        """Gets a peer profile instance from the list of profiles"""
        for i in self.peerProfiles:
            # if the peer's profile is already loaded, return that
            if i.address == peer:
                retData = i
                break
        else:
            # if the peer's profile is not loaded, return a new one.
            # connectNewPeer also adds it to the list on connect
            retData = onionrpeers.PeerProfiles(peer)
            self.peerProfiles.append(retData)
        return retData

    def getUptime(self):
        return epoch.get_epoch() - self.startTime

    def heartbeat(self):
        """Show a heartbeat debug message."""
        logger.debug('Heartbeat. Node running for %s.' %
                     humanreadabletime.human_readable_time(self.getUptime()))
        self.decrementThreadCount('heartbeat')


def startCommunicator(shared_state):
    OnionrCommunicatorDaemon(shared_state)

