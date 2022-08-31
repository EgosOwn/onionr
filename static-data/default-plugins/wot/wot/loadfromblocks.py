from typing import Generator
import blockdb

from .identity import Identity


def load_identities_from_blocks(blocks) -> Generator[Identity]:
    for block in blockdb.get_blocks_by_type('wotb'):
        yield Identity.deserialize(block.data)
