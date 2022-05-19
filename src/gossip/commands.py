from enum import IntEnum, auto

class GossipCommands(IntEnum):
    PING = 1
    ANNOUNCE = auto()
    PEER_EXCHANGE = auto()
    STREAM_BLOCKS = auto()
    PUT_BLOCKS = auto()


def command_to_byte(cmd: GossipCommands):
    return int(cmd).to_bytes(1, 'big')
