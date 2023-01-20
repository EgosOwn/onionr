from typing import TYPE_CHECKING

import result
import nacl.signing
import nacl.exceptions

if TYPE_CHECKING:
    from identity import Identity


def create_signature_by_identity(
        identity: 'Identity', message: bytes) -> result.Result[nacl.signing.SignedMessage]:
    return result.as_result(nacl.exceptions.CryptoError)(identity.private_key.sign)(message)


def verify_signature_by_identity(
        identity: 'Identity', 
        message: bytes, signature: bytes) -> result.Result[str]:
    return result.as_result(nacl.exceptions.CryptoError)(nacl.signing.verify)(
        identity.key, message, signature)
