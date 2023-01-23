import traceback
from gossip.commands import GossipCommands, command_to_byte
from .peerset import gossip_peer_set

from logger import log as logging


def connect_peer(peer):
    if peer in gossip_peer_set:
        return
    try:
        s = peer.get_socket(120)
    except Exception:
        logging.debug(f"Could not connect to {peer.transport_address}")
        logging.debug(traceback.format_exc())
    else:
        with s:
            s.sendall(command_to_byte(GossipCommands.PING))

            if s.recv(4).decode('utf-8') == 'PONG':
                gossip_peer_set.add(peer)
                logging.info(f"connected to {peer.transport_address}")
