import threading
from time import sleep
from typing import TYPE_CHECKING, Set, Tuple

if TYPE_CHECKING:
    from ordered_set import OrderedSet
    from onionrblocks import Block
    from queue import Queue

    from .peer import Peer

from onionrthreads import add_onionr_thread
import onionrplugins
import logger

from .connectpeer import connect_peer
from .client import gossip_client
from .server import gossip_server
from .constants import BOOTSTRAP_ATTEMPTS
from .peerset import gossip_peer_set
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


def start_gossip_threads():
    # Peer set is largely handled by the transport plugins
    # There is a unified set so gossip logic is not repeated

    add_onionr_thread(
        gossip_server, 1, initial_sleep=0.2)

    threading.Thread(
        target=gossip_client, daemon=True).start()
    onionrplugins.events.event('gossip_start', data=None, threaded=True)
    for _ in range(BOOTSTRAP_ATTEMPTS):
        onionrplugins.events.event(
            'bootstrap', data={'callback': connect_peer},
            threaded=False)
        sleep(60)
        if len(gossip_peer_set):
            return
    logger.error("Could not connect to any peers :(", terminal=True)
