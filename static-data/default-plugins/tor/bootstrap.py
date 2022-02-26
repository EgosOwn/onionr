from threading import Thread
from time import sleep
import os

from gossip.peer import Peer
import logger
import config
from getsocks import get_socks

from torpeer import TorPeer
from torfilepaths import control_socket

bootstrap_file = f'{os.path.dirname(os.path.realpath(__file__))}/bootstrap.txt'

def on_bootstrap(api, data):

    try:
        with open(bootstrap_file, 'r') as bootstrap_file_obj:
            bootstrap_nodes = set(bootstrap_file_obj.read().split(','))
    except FileNotFoundError:
        bootstrap_nodes = set()

    while not os.path.exists(control_socket):
        sleep(0.1)

    while not config.get('tor.transport_address'):
        sleep(1)
        config.reload()

    socks_address, socks_port = get_socks()[0]

    for address in bootstrap_nodes:
        if address == config.get('tor.transport_address'):
            continue
        if not address.endswith('.onion'):
            address += '.onion'
        # Tell the gossip logic that this peer is ready to connect
        # it will add it to data['peer_set'] if it responds to ping
        Thread(
            target=data['callback'],
            args=[data['peer_set'], TorPeer(socks_address, socks_port, address)],
            daemon=True).start()


