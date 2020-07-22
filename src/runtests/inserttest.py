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
    time.sleep(0.3)
    if b_hash not in testmanager._too_many.get_by_string("PublicAPI").hideBlocks:
        raise ValueError("Block not hidden")

    if b_hash not in coredb.blockmetadb.get_block_list():
        logger.error(str(b_hash) + 'is not in bl')
        raise ValueError
