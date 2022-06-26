from os.path import exists
from socket import AF_UNIX, SOCK_STREAM, socket

class UnixPeer:

    def __init__(self, socket_file):

        if not exists(socket_file):
            raise FileExistsError("No such file " + socket_file)

        self.transport_address = socket_file


    def get_socket(self, connect_timeout) -> socket:

        s = socket(AF_UNIX, SOCK_STREAM)
        #s.settimeout(connect_timeout)
        s.connect(self.transport_address)
        return s

    def __hash__(self):
        return hash(self.transport_address)

    def __eq__(self, other):
        try:
            return self.transport_address == other.transport_address
        except AttributeError:
            return False
