from enum import IntEnum, auto
from types import SimpleNamespace

class WotCommand(IntEnum):
    TRUST = 1
    REVOKE_TRUST = auto()
    ANNOUNCE = auto()
    REVOKE = auto()


_block_type_map = {
    'trust': b'wots'
}

block_type_map = SimpleNamespace(**_block_type_map)