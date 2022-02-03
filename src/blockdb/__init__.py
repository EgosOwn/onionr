from typing import Generator

from onionrblocks import Block

import db
from .. import identifyhome

block_db_path = identifyhome.identify_home() + 'blocks.db'


def get_blocks_by_type(block_type) -> Generator[Block]:
    block_db = db.get_db_obj(block_db_path, 'u')
    for block_hash in db.list_keys(block_db_path):
        block = Block(block_hash, block_db[block_hash], auto_verify=False)
        if block.type == block_type:
            yield block
