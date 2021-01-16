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
from . import onlinepeers
from . import uploadqueue
from communicatorutils import downloadblocks
from communicatorutils import lookupblocks
from communicatorutils import lookupadders
from communicatorutils import connectnewpeers
from communicatorutils import uploadblocks
from communicatorutils import announcenode, deniableinserts
from communicatorutils import cooldownpeer
from communicatorutils import housekeeping
from communicatorutils import netcheck
from onionrthreads import add_onionr_thread
from onionrcommands.openwebinterface import get_url
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

config.reload()


class OnionrCommunicatorDaemon:
    def __init__(self, shared_state, developmentMode=None):
        if developmentMode is None:
            developmentMode = config.get(
                'general.dev_mode', False)

        # configure logger and stuff
        self.config = config
        self.shared_state = shared_state  # TooManyObjects module
        shared_state.add(self)

        # populate kv values
        self.kv = self.shared_state.get_by_string('DeadSimpleKV')

        if config.get('general.offline_mode', False):
            self.kv.put('isOnline', False)

        # initialize core with Tor socks port being 3rd argument
        self.proxyPort = shared_state.get(NetController).socksPort

        self.upload_session_manager = self.shared_state.get(
            uploadblocks.sessionmanager.BlockUploadSessionManager)
        self.shared_state.share_object()

        # loop time.sleep delay in seconds
        self.delay = 5

        # amount of threads running by name, used to prevent too many
        self.threadCounts = {}

        # Loads in and starts the enabled plugins
        plugins.reload()

        # extends our upload list and saves our list when Onionr exits
        uploadqueue.UploadQueue(self)

        add_onionr_thread(
            lookupblocks.lookup_blocks_from_communicator,
            [self.shared_state], 25, 3)

        add_onionr_thread(
            downloadblocks.download_blocks_from_communicator,
            [self.shared_state],
            config.get('timers.getBlocks', 10), 1)

        add_onionr_thread(onlinepeers.clear_offline_peer, [self.kv], 58)

        add_onionr_thread(
            housekeeping.clean_old_blocks, [self.shared_state], 10, 1)

        # Discover new peers
        add_onionr_thread(
            lookupadders.lookup_new_peer_transports_with_communicator,
            [shared_state], 60, 3)

        # Timer for adjusting which peers
        # we actively communicate to at any given time,
        # to avoid over-using peers
        add_onionr_thread(
            cooldownpeer.cooldown_peer, [self.shared_state], 30, 60)

        # Timer to read the upload queue and upload the entries to peers
        add_onionr_thread(
            uploadblocks.upload_blocks_from_communicator,
            [self.shared_state], 5, 1)

        # This timer creates deniable blocks,
        # in an attempt to further obfuscate block insertion metadata
        if config.get('general.insert_deniable_blocks', True):
            add_onionr_thread(
                deniableinserts.insert_deniable_block, [], 180, 10)

        if config.get('transports.tor', True):
            # Timer to check for connectivity,
            # through Tor to various high-profile onion services
            add_onionr_thread(netcheck.net_check, [shared_state], 500, 60)

        # Announce the public API server transport address
        # to other nodes if security level allows
        if config.get('general.security_level', 1) == 0 \
                and config.get('general.announce_node', True):
            # Default to high security level incase config breaks
            add_onionr_thread(
                announcenode.announce_node, [self.shared_state], 600, 60)
        else:
            logger.debug('Will not announce node.')

        add_onionr_thread(onionrpeers.peer_cleanup, [], 300, 300)

        add_onionr_thread(housekeeping.clean_keys, [], 15, 1)

        if config.get('general.use_bootstrap_list', True):
            bootstrappeers.add_bootstrap_list_to_peer_list(
                self.kv, [], db_only=True)

        daemoneventhooks.daemon_event_handlers(shared_state)

        get_url()
        if not config.get('onboarding.done', True):
            logger.info(
                'First run detected. Run openhome to get setup.',
                terminal=True)

            while not config.get('onboarding.done', True) and \
                    not self.shared_state.get_by_string(
                        'DeadSimpleKV').get('shutdown'):
                try:
                    time.sleep(2)
                except KeyboardInterrupt:
                    self.shared_state.get_by_string(
                        'DeadSimpleKV').put('shutdown', True)

        # Main daemon loop, mainly for calling timers,
        # don't do any complex operations here to avoid locking
        try:
            while not self.shared_state.get_by_string(
                    'DeadSimpleKV').get('shutdown'):
                time.sleep(self.delay)
        except KeyboardInterrupt:
            self.shared_state.get_by_string(
                    'DeadSimpleKV').put('shutdown', True)

        logger.info(
            'Goodbye. (Onionr is cleaning up, and will exit)', terminal=True)

    def decrementThreadCount(self, threadName):
        """Decrement amount of a thread name if more than zero.

        called when a function meant to be run in a thread ends
        """
        try:
            if self.threadCounts[threadName] > 0:
                self.threadCounts[threadName] -= 1
        except KeyError:
            pass

    def peerCleanup(self):
        """This just calls onionrpeers.cleanupPeers.

        Remove dead or bad peers (offline too long, too slow)"""
        onionrpeers.peer_cleanup()
        self.decrementThreadCount('peerCleanup')

    def getPeerProfileInstance(self, peer):
        """Gets a peer profile instance from the list of profiles"""
        for i in self.kv.get('peerProfiles'):
            # if the peer's profile is already loaded, return that
            if i.address == peer:
                retData = i
                break
        else:
            # if the peer's profile is not loaded, return a new one.
            # connectNewPeer also adds it to the list on connect
            retData = onionrpeers.PeerProfiles(peer)
            self.kv.get('peerProfiles').append(retData)
        return retData


def startCommunicator(shared_state):
    OnionrCommunicatorDaemon(shared_state)
