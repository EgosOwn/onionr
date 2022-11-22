import keyring

import wot.identity


def get_identity_by_name(name: str) -> 'Identity':
    iden_key = keyring.get_credential('onionr.wot', name)
    if not iden_key:
        raise KeyError('Identity not found')
    return wot.identity.Identity(iden_key, name)


def set_identity_by_name(identity: 'Identity', name: str) -> None:
    if identity.private_key:
        keyring.set_credential('onionr.wot', name, identity.private_key)
    else:
        raise ValueError('Cannot set identity with no private key')

