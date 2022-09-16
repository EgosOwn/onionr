from typing import TYPE_CHECKING, Union

from nacl.signing import VerifyKey

if TYPE_CHECKING:
    from identity import Identity

from identity.identityset import identities


def get_identity_by_key(
        key: Union[bytes, 'VerifyKey']) -> 'Identity':

    if not isinstance(key, VerifyKey):
        key = VerifyKey(key)
    for identity in identities:
        if bytes(identity.key) == bytes(key):
            return identity
    raise KeyError("Identity not found")
