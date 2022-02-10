from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import queue
    from onionrblocks import Block

from onionrthreads import add_onionr_thread
"""
Onionr uses a flavor of Dandelion++ epidemic routing

The starter creates a peer set and passes it to the client and server
as well as each of the plugins.

The transports forward incoming requests to the gossip server

When a new peer announcement is recieved an event is fired and the transport plugin that handles it will (or wont)
create a new peer object by connecting to that peer

When a new block is generated, it is added to a queue in raw form passed to the starter


"""

def start_gossip_threads(block_queue: queue.Queue[Block]):
    # Peer set is largely handled by the transport plugins
    # There is a unified set so gossip logic is not repeated
    peer_set = set()


