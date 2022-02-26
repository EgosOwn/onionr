import logger


def connect_peer(peer_set, peer):
    try:
        peer.get_socket()
    except Exception:
        logger.warn(f"Could not connect to {peer.transport_address}")
    else:
        peer_set.add(peer)
        logger.info(f"connected to {peer.transport_address}")
