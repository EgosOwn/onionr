from secrets import token_bytes
from typing import TYPE_CHECKING
import socket

if TYPE_CHECKING:
    from stem.control import Controller

from onionrtypes import OnionAddressString

import yam


def peer_tunnel(tor_controller: Controller, peer):
    socks_port = tor_controller.get_conf('SocksPort')

    class Connected:
        connected = False

    send_buffer = []
    rec_buffer = []
    rec_address = None

    yam.client(1, peer, socks_port, send_buffer, rec_buffer, Connected)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ip = '127.0.0.1'
        s.bind((ip, 0))
        s.listen(1)
        port = s.getsockname()[1]
        serv = tor_controller.create_ephemeral_hidden_service(
                {1337: '127.0.0.1:' + str(port)},
                key_content='ED25519-V3',
                await_publication=True,
            )
        rec_address = serv.service_id
        conn, addr = s.accept()
        yam.server(1, tor_controller, conn, send_buffer, rec_buffer, Connected)


