from typing import Set

from onionrblocks import Block

from logger import log as logging

from .deleteblock import delete_block
from .getblocks import get_blocks_after_timestamp


def clean_block_database():
    """Delete expired blocks from block db"""
    remove_set: Set[bytes] = set()
    block: Block

    for block in get_blocks_after_timestamp(0):
        try:
            Block(block.id, block.raw, auto_verify=True)
        except ValueError:  # block expired
            remove_set.add(block)

    if len(remove_set):
        logging.info(f"Cleaning {len(remove_set)} blocks")
        [i for i in map(delete_block, remove_set)]
