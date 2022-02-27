from gossip.commands import GossipCommands, command_to_byte
import logger


def connect_peer(peer_set, peer):
    if peer in peer_set:
        return
    try:
        s = peer.get_socket()
    except Exception:
        logger.warn(f"Could not connect to {peer.transport_address}")
    else:
        s.sendall(command_to_byte(GossipCommands.CLOSE))
        s.close()
        peer_set.add(peer)
        logger.info(f"connected to {peer.transport_address}")
