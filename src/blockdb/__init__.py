from onionrblocks import Block

import db
from utils import identifyhome

block_db_path = identifyhome.identify_home() + 'blockdata'



def store_vdf_block(block: Block):
    db.set(block_db_path, block.id, block.raw)


def get_blocks_by_type(block_type: str):
    block_db = db.get_db_obj(block_db_path, 'u')
    for block_hash in db.list_keys(block_db_path):
        block = Block(block_hash, block_db[block_hash], auto_verify=False)
        if block.type == block_type:
            yield block


def get_blocks_after_timestamp(timestamp: int, block_type: str = ''):
    block_db = db.get_db_obj(block_db_path, 'u')

    for block_hash in db.list_keys(block_db_path):
        block = Block(block_hash, block_db[block_hash], auto_verify=False)
        if block.timestamp > timestamp:
            if block_type:
                if block_type == block.type:
                    yield block
            else:
                yield block
