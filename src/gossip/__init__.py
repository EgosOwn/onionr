from time import sleep
from typing import TYPE_CHECKING, Set
from os import urandom
import queue

if TYPE_CHECKING:
    from onionrblocks import Block

    from .peer import Peer

from onionrthreads import add_onionr_thread
import onionrplugins

from .client import gossip_client
from .server import gossip_server
from .commands import GossipCommands
"""
Onionr uses a flavor of Dandelion++ epidemic routing

The starter creates a peer set and passes it to the client and server
as well as each of the plugins.

The transports forward incoming requests to the gossip server

When a new peer announcement is recieved an event is fired and the transport
plugin that handles it will (or wont) create a new peer object by connecting
to that peer

When a new block is generated, it is added to a queue in raw form passed to
the starter

In stem phase, client uploads recieved (stem) blocks to 2 random peers.
In stem phase, server disables diffusion

"""


def start_gossip_threads(
        peer_set: Set['Peer'], block_queue: queue.Queue['Block']):
    # Peer set is largely handled by the transport plugins
    # There is a unified set so gossip logic is not repeated
    seed = urandom(32)

    add_onionr_thread(
        gossip_server, 1, peer_set, block_queue, seed, initial_sleep=0.2)
    add_onionr_thread(
        gossip_client, 1, peer_set, block_queue, seed, initial_sleep=0)
    onionrplugins.events.event('gossip_start', data=peer_set, threaded=True)
    sleep(4)
    onionrplugins.events.event('bootstrap', data=peer_set)
