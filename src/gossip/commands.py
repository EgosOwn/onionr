from enum import Enum, auto

class GossipCommands(Enum):
    PING = 1
    ANNOUNCE = auto()
    PEER_EXCHANGE = auto()
    STREAM_BLOCKS = auto()
    PUT_BLOCKS = auto()

