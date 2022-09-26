import shelve
from gossip.peerset import gossip_peer_set

from torpeer import TorPeer
from torfilepaths import peer_database_file


def on_shutdown_event(api, data=None):
    with shelve.open(peer_database_file, 'c') as db:
        for peer in gossip_peer_set:
            if isinstance(peer, TorPeer):
                db[peer.onion_address] = peer
