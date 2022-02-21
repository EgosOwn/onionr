import socks


class TorPeer:

    def __init__(self, socks_host, socks_port, onion_address):
        self.onion_address = onion_address
        self.socks_host = socks_host
        self.socks_port = socks_port

    def get_socket(self) -> socks.socksocket:
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS4, self.socks_host, self.socks_port, rdns=True)
        s.connect((self.onion_address, 80))
        return s
