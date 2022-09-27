import config
from logger import log as logging
from gossip.server import gossip_server_socket_file

from unixpeer import UnixPeer


def on_announce_rec(api, data=None):

    announced: str = data['address']
    try:
        announced = announced.decode('utf-8')
    except AttributeError:
        pass
    announced = announced.strip()
    if not announced.endswith('.sock'):
        return

    if announced == gossip_server_socket_file:
        return

    logging.info(f"Peer {announced} announced to us.")

    data['callback'](UnixPeer(announced))
