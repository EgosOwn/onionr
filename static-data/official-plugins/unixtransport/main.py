"""Onionr - Private P2P Communication.

Unix transport plugin. Intended for testing Onionr networks using IPC
"""
import sys
import os
import locale
from time import sleep
from logger import log as logging
from typing import Set, TYPE_CHECKING
from threading import Thread
import shelve

import stem
from stem.control import Controller

from utils import readstatic
import config
from filepaths import gossip_server_socket_file

from gossip.peer import Peer
from gossip.peerset import gossip_peer_set

locale.setlocale(locale.LC_ALL, '')
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# import after path insert
from unixpeer import UnixPeer

from unixbootstrap import on_bootstrap
from unixannounce import on_announce_rec
from unixfilepaths import peer_database_file
#from shutdown import on_shutdown_event

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


plugin_name = 'unixtransport'
PLUGIN_VERSION = '0.0.0'


def on_shutdown_event(api, data=None):
    with shelve.open(peer_database_file, 'c') as db:
        for peer in gossip_peer_set:
            if isinstance(peer, UnixPeer):
                db[peer.transport_address] = peer

def on_init(api, data=None):
    logging.info(
        f"Unix Transport Plugin v{PLUGIN_VERSION} enabled")
    logging.info(
        f"Peers can connect to {gossip_server_socket_file}")

def on_get_our_transport(api, data=None):
    callback_func = data['callback']
    for_peer = data['peer']
    if for_peer.transport_address == gossip_server_socket_file:
        return
    if data['peer'].__class__ == UnixPeer:
        callback_func(for_peer, gossip_server_socket_file)
