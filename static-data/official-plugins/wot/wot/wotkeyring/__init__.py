import base64

import keyring
import nacl.signing

import wot.identity


def get_identity_by_name(name: str) -> 'Identity':
    iden_key = keyring.get_credential('onionr.wot', name)
    if not iden_key:
        raise KeyError('Identity not found')
    iden_key = base64.b85decode(iden_key.password)
    iden_key = nacl.signing.SigningKey(iden_key)

    return wot.identity.Identity(iden_key, name)


def set_identity(identity: 'Identity') -> None:
    name = identity.name
    if identity.private_key:
        keyring.set_password('onionr.wot', name, base64.b85encode(bytes(identity.private_key)))
    else:
        raise ValueError('Cannot set identity with no private key')

