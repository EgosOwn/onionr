from typing import TYPE_CHECKING
from typing import Set

from queue import Queue

if TYPE_CHECKING:
    from onionrblocks import Block
    from peer import Peer


def gossip_client(peer_set: Set[Peer], block_queue: Queue[Block]):
    return
