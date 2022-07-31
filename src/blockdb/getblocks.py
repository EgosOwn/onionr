from typing import Generator

import db

from onionrblocks import Block

from .dbpath import block_db_path

def get_blocks_by_type(block_type: str) -> "Generator[Block]":
    block_db = db.get_db_obj(block_db_path, 'u')
    for block_hash in db.list_keys(block_db_path):
        block = Block(block_hash, block_db[block_hash], auto_verify=False)
        if block.type == block_type:
            yield block


def get_blocks_after_timestamp(
        timestamp: int, block_type: str = '') -> "Generator[Block]":
    block_db = db.get_db_obj(block_db_path, 'u')

    for block_hash in db.list_keys(block_db_path):
        block = Block(block_hash, block_db[block_hash], auto_verify=False)
        if block.timestamp > timestamp:
            if block_type:
                if block_type == block.type:
                    yield block
            else:
                yield block