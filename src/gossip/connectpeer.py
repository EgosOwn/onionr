from gossip.commands import GossipCommands, command_to_byte
from .peerset import gossip_peer_set

import logger


def connect_peer(peer):
    if peer in gossip_peer_set:
        return
    try:
        s = peer.get_socket(15)
    except Exception:
        logger.warn(f"Could not connect to {peer.transport_address}")
    else:
        s.sendall(command_to_byte(GossipCommands.PING))
        if s.recv(5).decode('utf-8') == 'PONG':
            gossip_peer_set.add(peer)
            logger.info(f"connected to {peer.transport_address}")
        s.close()
