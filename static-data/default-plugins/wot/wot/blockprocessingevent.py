from typing import TYPE_CHECKING
from enum import IntEnum, auto
import struct

import msgpack

if TYPE_CHECKING:
    from onionrblocks import Block

from .exceptions import InvalidWotBlock


class WotCommand(IntEnum):
    TRUST = 1
    UNTRUST = auto()
    ANNOUNCE = auto()
    REVOKE = auto()


class WotPayload:
    def __init__(self, block_data: bytes):
        wot_command = WotCommand(
            int.from_bytes(block_data[0], byteorder='big'))


        match wot_command(WotCommand):
            case WotCommand.TRUST:
                pass


def process_block(bl: 'Block'):
    assert bl.type == 'iden'
    wot_command = WotCommand(bl.data)
