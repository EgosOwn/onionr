from enum import IntEnum, auto

class GossipCommands(IntEnum):
    PING = 1
    ANNOUNCE = auto()
    PEER_EXCHANGE = auto()
    STREAM_BLOCKS = auto()
    PUT_BLOCKS = auto()
    CLOSE = auto()

