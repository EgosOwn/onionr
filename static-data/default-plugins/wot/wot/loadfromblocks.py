from typing import Generator
import traceback

from nacl.signing import VerifyKey
import nacl.exceptions

import logger
import blockdb

from wot.identity import Identity, processtrustsignature, identities
from wot.exceptions import IdentitySerializationError
from wot.getbykey import get_identity_by_key


def load_identity_from_block(block) -> Identity:
    return Identity.deserialize(block.data)


def load_identities_from_blocks() -> Generator[Identity, None, None]:
    for block in blockdb.get_blocks_by_type(b'wotb'):
        try:
            yield load_identity_from_block(block)
        except IdentitySerializationError:
            pass


def load_signatures_from_blocks() -> None:
    for block in blockdb.get_blocks_by_type(b'wots'):
        try:
            # If good signature,
            # it adds the signature to the signed identity's trust set
            # noop if already signed
            processtrustsignature.process_trust_signature(block.data)
        except nacl.exceptions.BadSignatureError:
            logger.warn('Bad signature in block:')
            logger.warn(traceback.format_exc())
