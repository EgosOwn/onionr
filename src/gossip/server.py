from typing import TYPE_CHECKING
from typing import Set

from queue import Queue

if TYPE_CHECKING:
    from onionrblocks import Block
    from peer import Peer

from filepaths import gossip_server_socket_file

import asyncio



def gossip_server(
        peer_set: Set['Peer'],
        block_queue: Queue['Block'],
        dandelion_seed: bytes):
    return