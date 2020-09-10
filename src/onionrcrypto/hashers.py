import hashlib

import nacl.hash


def sha3_hash(data):
    try:
        data = data.encode()
    except AttributeError:
        pass
    hasher = hashlib.sha3_256()
    hasher.update(data)
    return hasher.hexdigest()


def blake2b_hash(data):
    try:
        data = data.encode()
    except AttributeError:
        pass
    return nacl.hash.blake2b(data)
