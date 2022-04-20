import config
import logger

from getsocks import get_socks
from torpeer import TorPeer


def on_announce_rec(api, data=None):
    socks_address, socks_port = get_socks()[0]

    announced = data['address']
    try:
        announced = announced.decode('utf-8')
    except AttributeError:
        pass

    if announced == config.get('tor.transport_address'):
        logger.warn(
            "Received announcement for our own node, which shouldn't happen")
        return

    announced = announced.strip()
    announced += '.onion'

    data['callback'](TorPeer(socks_address, socks_port, announced))
