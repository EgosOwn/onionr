from typing import Generator
import blockdb

from identity import Identity
from exceptions import IdentitySerializationError


def load_identity_from_block(block) -> Identity:
    return Identity.deserialize(block.data)


def load_identities_from_blocks() -> Generator[Identity, None, None]:
    for block in blockdb.get_blocks_by_type(b'wotb'):
        try:
            yield load_identity_from_block(block)
        except IdentitySerializationError:
            pass
