from typing import Protocol


class Peer(Protocol):
    stats = {}
    sock = None
    id = ""
    node_address = ""

    def __init__(self):
        return
    def get_socket(self):
        return

    def disconnect(self):
        return
