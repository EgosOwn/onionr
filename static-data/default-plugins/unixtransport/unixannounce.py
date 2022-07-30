import config
import logger
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

    logger.info(f"Peer {announced} announced to us.", terminal=True)

    data['callback'](UnixPeer(announced))
