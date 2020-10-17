"""Onionr - Private P2P Communication.

read from a file from an offset (efficiently)
"""
from collections import namedtuple

OffsetReadResult = namedtuple('OffsetReadResult', ['data', 'new_offset'])


def read_from_offset(file_path, offset=0):
    with open(file_path, 'rb') as f:
        if offset:
            f.seek(offset)
        data = f.read()
        offset = f.tell()

    return OffsetReadResult(data, offset)
