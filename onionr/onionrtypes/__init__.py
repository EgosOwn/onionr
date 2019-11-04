from typing import NewType

UserID = NewType('UserID', str)
UserIDSecretKey = NewType('UserIDSecretKey', str)

DeterministicKeyPassphrase = NewType('DeterministicKeyPassphrase', str)

BlockHash = NewType('BlockHash', str)