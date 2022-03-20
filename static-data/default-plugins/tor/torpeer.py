import socks


class TorPeer:

    def __init__(self, socks_host, socks_port, onion_address):
        if not onion_address or onion_address == '.onion':
            raise ValueError("Invalid transport address")
        self.transport_address = self.onion_address = onion_address
        self.socks_host = socks_host
        self.socks_port = socks_port

    def get_socket(self, connect_timeout) -> socks.socksocket:
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS4, self.socks_host, self.socks_port, rdns=True)
        s.settimeout(connect_timeout)
        s.connect((self.onion_address, 80))
        return s

    def __hash__(self):
        return hash(self.transport_address)

    def __eq__(self, other):
        try:
            return self.transport_address == other.transport_address
        except AttributeError:
            return False
