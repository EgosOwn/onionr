from typing import TYPE_CHECKING

from onionrthreads import add_onionr_thread
from communicator.onlinepeers import get_online_peers
from communicatorutils import lookupblocks
from communicatorutils import downloadblocks
from communicator import onlinepeers
from communicatorutils import housekeeping
from communicatorutils import lookupadders
from communicatorutils import cooldownpeer
from communicatorutils import uploadblocks
from communicatorutils import announcenode, deniableinserts
from communicatorutils import netcheck
import onionrpeers

import config

if TYPE_CHECKING:
    from deadsimplekv import DeadSimpleKV
    from toomanyobjs import TooMany



def spawn_client_threads(shared_state: 'TooMany'):
    kv: 'DeadSimpleKV' = shared_state.get_by_string('DeadSimpleKV')
    add_onionr_thread(get_online_peers, (shared_state,), 3, 1)

    add_onionr_thread(
        lookupblocks.lookup_blocks_from_communicator,
        [shared_state], 25, 3)
    add_onionr_thread(
        downloadblocks.download_blocks_from_communicator,
        [shared_state],
        config.get('timers.getBlocks', 10), 1)
    add_onionr_thread(onlinepeers.clear_offline_peer, [kv], 58)
    add_onionr_thread(
        housekeeping.clean_old_blocks, [shared_state], 10, 1)
    add_onionr_thread(housekeeping.clean_keys, [], 15, 1)
    # Discover new peers
    add_onionr_thread(
        lookupadders.lookup_new_peer_transports_with_communicator,
        [shared_state], 60, 3)
    # Thread for adjusting which peers
    # we actively communicate to at any given time,
    # to avoid over-using peers
    add_onionr_thread(
        cooldownpeer.cooldown_peer, [shared_state], 30, 60)
    # Thread to read the upload queue and upload the entries to peers
    add_onionr_thread(
        uploadblocks.upload_blocks_from_communicator,
        [shared_state], 5, 1)
    # This Thread creates deniable blocks,
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
            announcenode.announce_node, [shared_state], 600, 60)
    add_onionr_thread(onionrpeers.peer_cleanup, [], 300, 300)
