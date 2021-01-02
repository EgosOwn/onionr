"""Onionr - Private P2P Communication.

Create required Onionr directories
"""
from typing import Union
import dbm

from .securestring import generate_key_file, protect_string, unprotect_string
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


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


