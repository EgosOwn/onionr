from typing import Callable, Generator, List

from onionrblocks import Block
from onionrplugins import onionrevents

import db

from .dbpath import block_db_path
from .blockcleaner import clean_block_database
from .getblocks import get_blocks_after_timestamp, get_blocks_by_type
from .deleteblock import delete_block

block_storage_observers: List[Callable] = []




def add_block_to_db(block: Block):
    onionrevents.event('before_block_db_add', block, threaded=False)
    db.set_if_new(block_db_path, block.id, block.raw) # Raises db.DuplicateKey if dupe
    onionrevents.event('after_block_db_add', block, threaded=False)


def has_block(block_hash):
    return block_hash in db.list_keys(block_db_path)


def get_block(block_hash) -> Block:
    return Block(
        block_hash,
        db.get_db_obj(block_db_path, 'u').get(block_hash),
        auto_verify=False)

