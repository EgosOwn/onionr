from typing import TYPE_CHECKING, Iterable, Union

from nacl.signing import VerifyKey

if TYPE_CHECKING:
    from identity import Identity

from identityset import identities


def get_identity_by_key(
        key: Union[bytes, 'VerifyKey']) -> 'Identity':

    if not isinstance(key, VerifyKey):
        key = VerifyKey(key)
    for identity in identities:
        if bytes(identity.key) == bytes(key):
            return identity
    raise KeyError("Identity not found")
