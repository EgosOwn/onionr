import os

import onionrblocks
import logger
import coredb
from onionrutils import epoch

def stress_test_block_insert(testmanager):
    return
    start = epoch.get_epoch()
    count = 100
    max_insert_speed = 120
    for x in range(count): onionrblocks.insert(os.urandom(32))
    speed = epoch.get_epoch() - start
    if speed < max_insert_speed:
        raise ValueError(f'{count} blocks inserted too fast, {max_insert_speed}, got {speed}')
    logger.info(f'runtest stress block insertion: {count} blocks inserted in {speed}s')
