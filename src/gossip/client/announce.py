from time import sleep
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .. import Peer

import logger
import onionrplugins

from ..commands import GossipCommands, command_to_byte
from ..peerset import gossip_peer_set


def do_announce():
    "Announce with N peers of each identified transport"
    def _announce(announce_peer: 'Peer', our_transport_address: str):
        try:
            our_transport_address = our_transport_address.encode('utf-8') + b"\n"
        except AttributeError:
            pass
        sock = announce_peer.get_socket(12)
        sock.sendall(command_to_byte(GossipCommands.ANNOUNCE))
        sock.sendall(our_transport_address)
        if int.from_bytes(sock.recv(1), 'big') != 1:
            logger.warn(
                f"Could not announce with {announce_peer.transport_address}")
        sock.close()

    while not len(gossip_peer_set):
        sleep(1)

    per_transport = 3
    peer_types = {}
    count_for_peer = 0
    for peer in gossip_peer_set:
        try:
            count_for_peer = peer_types[peer.__class__]
        except KeyError:
            count_for_peer = peer_types[peer.__class__] = 0

        if count_for_peer == per_transport:
            continue

        # Plugin for the transport associated with the peer will call _announce
        # with the peer and *our* transport address
        onionrplugins.events.event(
            'get_our_transport',
            data={'callback': _announce, 'peer': peer},
            threaded=True)

        peer_types[peer.__class__] += 1
