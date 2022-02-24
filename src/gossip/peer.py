from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
    import socket


class Peer(Protocol):
    stats = {}
    sock = None
    id = ""
    node_address = ""

    def __init__(self):
        return
    def get_socket(self) -> 'socket.socket':
        return

    def disconnect(self):
        return
