import socks

from gossip.peerset import gossip_peer_set
import logger


class HandleRevc:
    def __init__(self, sock):
        self.sock_recv = sock.recv
        self.sock = sock

    def recv(self, *args, **kwargs):
        try:
            got_data = self.sock_recv(*args, **kwargs)
            if not len(got_data):
                raise ConnectionError("Peer socket returned empty value")
            return got_data
        except Exception:
            try:
                gossip_peer_set.remove(self.sock)
            except KeyError:
                pass
            raise


class TorPeer:

    def __init__(self, socks_host, socks_port, onion_address):
        if not onion_address or onion_address == '.onion':
            raise ValueError("Invalid transport address")
        if not onion_address.endswith('.onion'):
            self.onion_address = onion_address.strip() + '.onion'

        self.transport_address = self.onion_address = onion_address
        self.socks_host = socks_host
        self.socks_port = socks_port

    def get_socket(self, connect_timeout) -> socks.socksocket:

        s = socks.socksocket()
        s.set_proxy(socks.SOCKS4, self.socks_host, self.socks_port, rdns=True)
        s.settimeout(connect_timeout)
        try:
            s.connect((self.onion_address, 80))
        except socks.GeneralProxyError:
            try:
                gossip_peer_set.remove(self)
            except KeyError:
                pass
            else:
                logger.debug(
                    f"Could not create socket to peer {self.transport_address}",
                    terminal=True)
            raise TimeoutError
        mock_recv = HandleRevc(s)
        s.recv = mock_recv.recv
        return s

    def __hash__(self):
        return hash(self.transport_address)

    def __eq__(self, other):
        try:
            return self.transport_address == other.transport_address
        except AttributeError:
            return False
