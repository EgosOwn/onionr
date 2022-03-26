from typing import Callable, Generator, List

from onionrblocks import Block

import db

from .dbpath import block_db_path


block_storage_observers: List[Callable] = []


def add_block_to_db(block: Block):
    # Raises db.DuplicateKey if dupe
    db.set_if_new(block_db_path, block.id, block.raw)

    for func in block_storage_observers:
        func(block)


def get_blocks_by_type(block_type: str) -> Generator[Block]:
    block_db = db.get_db_obj(block_db_path, 'u')
    for block_hash in db.list_keys(block_db_path):
        block = Block(block_hash, block_db[block_hash], auto_verify=False)
        if block.type == block_type:
            yield block


def get_blocks_after_timestamp(
        timestamp: int, block_type: str = '') -> Generator[Block]:
    block_db = db.get_db_obj(block_db_path, 'u')

    for block_hash in db.list_keys(block_db_path):
        block = Block(block_hash, block_db[block_hash], auto_verify=False)
        if block.timestamp > timestamp:
            if block_type:
                if block_type == block.type:
                    yield block
            else:
                yield block
