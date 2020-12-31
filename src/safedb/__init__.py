from typing import Union
from enum import Enum, auto
import dbm

from filenuke import nuke

from .securestring import generate_key_file, protect_string, unprotect_string



class SafeDB:
    """Wrapper around dbm to optionally encrypt db values."""

    def get(self, key: Union[str, bytes, bytearray]) -> bytes:
        if self.protected:
            return self.db_conn[key]
        return unprotect_string(self.db_conn[key])

    def put(
            self, key: [str, bytes, bytearray], value: [bytes, bytearray]):
        if self.protected:
            self.db_conn[key] = protect_string(value)
        else:
            self.db_conn[key] = value

    def close(self):
        self.db_conn.close()

    def __init__(self, db_path: str, protected=True):
        self.db_path = db_path
        self.db_conn = dbm.open(db_path, "c")

        try:
            existing_protected_mode = self.db_conn['enc']
            if protected and existing_protected_mode != b'1':
                raise ValueError(
                    "Cannot open unencrypted database with protected=True")
            elif not protected and existing_protected_mode != b'0':
                raise ValueError(
                    "Cannot open encrypted database in protected=False")
        except KeyError:
            if protected:
                self.db_conn['enc'] = b'1'
            else:
                self.db_conn['enc'] = b'0'
            try:
                generate_key_file()
            except FileExistsError:
                pass

        self.protected = protected


