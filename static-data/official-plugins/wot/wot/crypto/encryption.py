from typing import TYPE_CHECKING, Union

from ..identity import Identity

import result
import nacl.exceptions
import nacl.public
import nacl.utils


@result.as_result(nacl.exceptions.CryptoError, AttributeError)
def encrypt_to_identity_anonymously(
        identity: 'Identity',
        message: Union[bytes, str]) -> nacl.utils.EncryptedMessage:
    
    their_public_key = identity.key.to_curve25519_public_key()
    box = nacl.public.SealedBox(their_public_key)

    try:
        message = message.encode('utf-8')
    except AttributeError:
        pass

    return box.encrypt(message)


@result.as_result(nacl.exceptions.CryptoError, AttributeError)
def decrypt_from_identity_anonymously(
        our_identity: 'Identity', message: bytes) -> bytes:
    
    our_private_key = our_identity.private_key.to_curve25519_private_key()
    box = nacl.public.SealedBox(our_private_key)

    return box.decrypt(message)


@result.as_result(nacl.exceptions.CryptoError, AttributeError)
def encrypt_to_identity(
        our_identity: 'Identity',
        identity: 'Identity',
        message: Union[bytes, str]) -> nacl.utils.EncryptedMessage:
    our_private_key = our_identity.private_key.to_curve25519_private_key()
    their_public_key = identity.key.to_curve25519_public_key()
    box = nacl.public.Box(our_private_key, their_public_key)

    try:
        message = message.encode('utf-8')
    except AttributeError:
        pass

    return box.encrypt(message)

@result.as_result(nacl.exceptions.CryptoError, AttributeError)
def decrypt_from_identity(
        our_identity: 'Identity',
        identity: 'Identity',
        message: bytes) -> bytes:
    our_private_key = our_identity.private_key.to_curve25519_private_key()
    their_public_key = identity.key.to_curve25519_public_key()
    box = nacl.public.Box(our_private_key, their_public_key)

    return box.decrypt(message)
