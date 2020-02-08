import os
import time

import onionrblocks
import logger
import coredb
from communicator import peeraction

def _check_remote_node(testmanager):
    return

def insert_bin_test(testmanager):
    data = os.urandom(32)
    b_hash = onionrblocks.insert(data)

    if not b_hash in coredb.blockmetadb.get_block_list():
        logger.error(str(b_hash) + 'is not in bl')
        raise ValueError
