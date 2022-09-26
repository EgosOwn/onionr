import config
import logger
from gossip.peerset import gossip_peer_set

from getsocks import get_socks
from torpeer import TorPeer

MAX_TOR_PEERS = 20

def on_announce_rec(api, data=None):
    announced: str = data['address']
    try:
        announced = announced.decode('utf-8')
    except AttributeError:
        pass
    announced = announced.strip()
    if not announced.endswith('.onion'):
        return
    socks_address, socks_port = get_socks()[0]


    if announced.replace('.onion', '') == config.get(
            'tor.transport_address', '').replace('.onion', ''):
        return


    logger.info(f"Peer {announced} announced to us.", terminal=True)

    data['callback'](TorPeer(socks_address, socks_port, announced))
