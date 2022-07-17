"""Onionr - Private P2P Communication.

Unix transport plugin. Intended for testing Onionr networks using IPC
"""
import sys
import os
import locale
from time import sleep
import traceback
from typing import Set, TYPE_CHECKING
from threading import Thread

import stem
from stem.control import Controller

import logger
from utils import readstatic
import config
from filepaths import gossip_server_socket_file

from gossip.peer import Peer

locale.setlocale(locale.LC_ALL, '')
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# import after path insert
from unixpeer import UnixPeer

from unixbootstrap import on_bootstrap
from unixannounce import on_announce_rec
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




def on_init(api, data=None):
    logger.info(
        f"Unix Transport Plugin v{PLUGIN_VERSION} enabled", terminal=True)
    logger.info(
        f"Peers can connect to {gossip_server_socket_file}", terminal=True)

def on_get_our_transport(api, data=None):
    callback_func = data['callback']
    for_peer = data['peer']
    if for_peer.transport_address == gossip_server_socket_file:
        return
    if data['peer'].__class__ == UnixPeer:
        callback_func(for_peer, gossip_server_socket_file)
