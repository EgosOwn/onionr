from typing import Union
from enum import Enum, auto

import dbm



class SafeDB:
    def safe_get(key: Union[str, bytes]) -> bytes:
        return

    def __enter__(self):
        self.db = dbm.open(self.db_path, "c")
        return self.db

    def __exit__(self):
        self.db.close()

    def __init__(self, db_path: str, use_):
        self.db_path = db_path


