from collections import deque
from enum import Enum
from typing import Set, Union
import time

from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import Base32Encoder
from nacl.exceptions import BadSignatureError

from wot.identity.name import IdentityName
from wot.identity.name import max_len as max_name_len
from wot.identity.identityset import IdentitySet, identities
from wot.exceptions import IdentitySerializationError
from wot.timestamp import WotTimestamp


short_identity_keys = {
    'trusted': 't',
    'name': 'n',
    'key': 'k'
}

class Identity:
    def __init__(
            self,
            key: Union[SigningKey, VerifyKey],
            name: 'IdentityName',
            created_date: WotTimestamp = None):
        self.trusted: Set[Identity] = IdentitySet()
        self.name = IdentityName(name)
        self.created_date = created_date

        self.private_key = self.key = None

        if isinstance(key, bytes):
            self.key = VerifyKey(key)

        # SigningKey and VerifyKey have minimal memory overhead
        # so we do not need to make them properties
        if isinstance(key, SigningKey):
            self.private_key = key
            self.key = key.verify_key
        elif isinstance(key, VerifyKey):
            self.key = key


    def __eq__(self, other):
        return self.key == other

    def __str__(self):
        return self.key.encode(encoder=Base32Encoder).decode('utf-8')

    def __hash__(self):
        return hash(self.key)

    def serialize(self) -> bytes:
        """
        A serialized identity is the name signed by the private key plus
        the public key
        """
        if not self.private_key:
            raise IdentitySerializationError("Cannot serialize public identity")
        signed = self.private_key.sign(
            self.name.zfill(max_name_len).encode('utf-8') + bytes(self.key) +
            str(int(time.time())).encode('utf-8'))

        return signed.signature + signed.message

    @classmethod
    def deserialize(cls, serialized: bytes):
        signature = serialized[:64]
        message = serialized[64:]
        name = message[:max_name_len].decode('utf-8').lstrip('0')
        key = VerifyKey(message[max_name_len:max_name_len + 32])
        date = WotTimestamp(message[max_name_len + 32:].decode('utf-8'))
        if date > time.time():
            raise IdentitySerializationError(
                "Date in serialized identity is in the future")
        elif date <= 0:
            raise IdentitySerializationError("Date in serialized identity is <= 0")
        try:
            VerifyKey.verify(key, message, signature)
        except BadSignatureError:
            raise IdentitySerializationError(
                "Signature in serialized identity is invalid")
        return cls(key, name)


def get_distance(identity: Identity, identity2: Identity):
    distance = 0
    visited = set()
    stack = deque([identity])

    while stack:
        current_iden = stack.popleft()

        if current_iden == identity2:
            return distance
        distance += 1

        if identity2 in current_iden.trusted:
            return distance

        for trusted in current_iden.trusted:
            if trusted not in visited:
                visited.add(trusted)
                stack.append(trusted)
    raise ValueError
