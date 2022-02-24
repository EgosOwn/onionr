from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .. import Peer

from ..commands import GossipCommands, command_to_byte
import onionrplugins


def do_announce(peer_set):
    "Announce with N peers of each identified transport"
    def _announce(announce_peer: 'Peer', our_transport_address: str):
        sock = announce_peer.get_socket()
        sock.send(
            command_to_byte(GossipCommands.ANNOUNCE) + our_transport_address)
        if sock.dup


    per_transport = 3
    peer_types = {}
    count_for_peer = 0
    for peer in peer_set:
        try:
            count_for_peer = peer_types[peer.__name__]
        except KeyError:
            peer_types[peer.__name__] = 0
            continue

        if count_for_peer == per_transport:
            continue

        onionrplugins.events.event(
            'get_our_transport',
            data={'callback': _announce, 'peer': peer})

        peer_types[peer.__name__] += 1
