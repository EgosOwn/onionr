import shelve
from threading import Thread
from time import sleep
import os
import dbm
import traceback
from typing import Callable

from gossip.server import gossip_server_socket_file
from gossip.peer import Peer
from gossip.peerset import gossip_peer_set
from utils.identifyhome import identify_home
from logger import log as logging
import config

from unixpeer import UnixPeer
from unixfilepaths import peer_database_file

bootstrap_file = f'{os.path.dirname(os.path.realpath(__file__))}/bootstrap.txt'


def load_existing_peers(callback: Callable):
    """Load peers saved to disk"""
    peer_address: str = ''

    # the peers here are saved on clean shutdown
    with shelve.open(peer_database_file, 'r') as unix_peer_db:
        peer_address: str = unix_peer_db.nextkey()
        while peer_address:
            Thread(
                target=callback,
                args=[unix_peer_db[peer_address]],
                name=f'{peer_address} connection attempt',
                daemon=True).start()


def on_bootstrap(api, data=None):
    callback_func = data['callback']

    try:
        load_existing_peers(callback_func)
    except dbm.error:
        try:
            with open(bootstrap_file, 'r') as bootstrap_file_obj:
                bootstrap_nodes = set(bootstrap_file_obj.read().split(','))
        except FileNotFoundError:
            bootstrap_nodes = set()
    except Exception as e:
        logging.warn(traceback.format_exc())
        return
    else:
        return

    while not os.path.exists(gossip_server_socket_file):
        sleep(0.1)

    for address in bootstrap_nodes:
        if address == gossip_server_socket_file or not address:
            continue

        if not os.path.exists(address):
            continue

        # Tell the gossip logic that this peer is ready to connect
        # it will add it to data['peer_set'] if it responds to ping
        Thread(
            target=callback_func,
            args=[UnixPeer(address)],
            daemon=True).start()
        sleep(1)

