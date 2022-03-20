from threading import Thread
from time import sleep
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from socket import socket

from onionrplugins import onionrevents

from ..peer import Peer
from ..commands import GossipCommands, command_to_byte
from ..constants import PEER_AMOUNT_TO_ASK, TRANSPORT_SIZE_BYTES
from .. import connectpeer

MAX_PEERS = 10


def _ask_peer(peer, peer_set):
    s: 'socket' = peer.get_socket(12)
    s.sendall(command_to_byte(GossipCommands.PEER_EXCHANGE))
    # Get 10 max peers
    for _ in range(MAX_PEERS):
        peer = s.recv(TRANSPORT_SIZE_BYTES)
        if not peer:
            break
        connect_data = {
            'address': peer,
            'callback': connectpeer.connect_peer,
            'peer_set': peer_set
        }
        onionrevents.event('announce_rec', data=connect_data, threaded=True)
    s.close()


def get_new_peers(peer_set):
    while not len(peer_set):
        sleep(0.5)

    # Deep copy the peer list
    peer_list: Peer = list(peer_set)
    peers_we_ask: Peer = []
    asked_count = 0

    while asked_count < PEER_AMOUNT_TO_ASK:
        try:
            peers_we_ask.append(peer_list.pop())
        except IndexError:
            break
        asked_count += 1

    if not len(peers_we_ask):
        raise ValueError("No peers present in pool during get_new_peers")
    peer_list.clear()  # Clear the deep copy so it doesn't occupy memory

    # Start threads to ask the peers for more peers
    threads = []
    for peer in peers_we_ask:
        t = Thread(target=_ask_peer, args=[peer, peer_set], daemon=True)
        t.start()
        threads.append(t)
    peers_we_ask.clear()
    # Wait for the threads to finish because this function is on a timer
    for thread in threads:
        thread.join()

