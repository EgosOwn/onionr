from typing import TYPE_CHECKING
from .identityprocessing import process_identity_announce

if TYPE_CHECKING:
    from onionrblocks import Block

from wot.exceptions import InvalidWotBlock
from wot.wotcommand import WotCommand


class WotPayload:
    def __init__(self, block_data: bytes):
        wot_command = WotCommand(
            int.from_bytes(block_data[0], byteorder='big'))


        match wot_command(WotCommand):
            case WotCommand.TRUST:
                pass
            case WotCommand.REVOKE_TRUST:
                pass
            case WotCommand.ANNOUNCE:
                process_identity_announce(block_data[1:])
            case WotCommand.REVOKE:
                pass
            case _:
                raise InvalidWotBlock('Invalid WOT command')


def process_block(bl: 'Block'):
    assert bl.type == 'iden'
    wot_command = WotCommand(bl.data)
