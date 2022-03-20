from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
    import socket


class Peer(Protocol):
    transport_address = ""

    def __init__(self):
        return
    def get_socket(self, connect_timeout) -> 'socket.socket':
        return

    def disconnect(self):
        return

    def __eq__(self, other):
        return

    def __hash__(self):
        """Use the transport address"""
        return