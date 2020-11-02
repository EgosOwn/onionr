import ujson
import nacl.utils
from nacl.public import PrivateKey, SealedBox

from .blockmetadata import get_block_metadata_from_data

def block_decrypt(raw_block) -> DecryptedBlock:
    block_header, user_meta, block_data = get_block_metadata_from_data(
        raw_block)
    

