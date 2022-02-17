"""Onionr - Private P2P Communication.

This default plugin handles "flow" messages
(global chatroom style communication)
"""
import sys
import os
import locale
import traceback
from typing import Set, TYPE_CHECKING
import base64

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
import starttor
from torpeer import TorPeer
from torfilepaths import control_socket
from getsocks import get_socks

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


plugin_name = 'tor'
PLUGIN_VERSION = '0.0.0'


bootstrap_file = f'{os.path.dirname(os.path.realpath(__file__))}/bootstrap.txt'

class OnionrTor:
    def __init__(self):
        return


def on_init(api, data=None):
    logger.info(
        f"Tor Transport Plugin v{PLUGIN_VERSION} enabled", terminal=True)


def on_bootstrap(api, data: Set[Peer] = None):
    bootstrap_nodes: Set[str]
    peers = data

    socks_address, socks_port = get_socks()

    try:
        with open(bootstrap_file, 'r') as bootstrap_file_obj:
            bootstrap_nodes = set(bootstrap_file_obj.read().split(','))
    except FileNotFoundError:
        bootstrap_nodes = set()

    for transport_address in bootstrap_nodes:
        if not transport_address.endswith('.onion'):
            transport_address += '.onion'
        tor_peer = TorPeer(socks_address, socks_port, transport_address)
        try:
            s = tor_peer.get_socket()
        except Exception as e:
            logger.warn(
                f"Could not connnect to Tor peer {transport_address} " +
                "see logs for more info",
                terminal=True)
            logger.warn(traceback.format_exc())
            continue
        peers.add(tor_peer)


def on_gossip_start(api, data: Set[Peer] = None):
    # We don't do gossip logic


    starttor.start_tor()

    with Controller.from_socket_file(control_socket) as controller:
        controller.authenticate()
        logger.info(
            "Tor socks is listening on " +
            f"{controller.get_listeners('SOCKS')}", terminal=True)
        key = config.get('tor.key')
        new_address = ''
        if not key:
            add_onion_resp = controller.create_ephemeral_hidden_service(
                {'80': f'unix:{gossip_server_socket_file}'},
                key_content='BEST', key_type='NEW')
            config.set('tor.key', add_onion_resp.private_key, savefile=True)
            new_address = 'Generated '
            config.set('tor.transport_address', add_onion_resp.service_id)
        else:
            try:
                add_onion_resp = controller.create_ephemeral_hidden_service(
                    {'80': f'unix:{gossip_server_socket_file}'},
                    key_content=key, key_type='ED25519-V3')
            except stem.ProtocolError:
                logger.error(
                    "Could not start Tor transport. Try restarting Onionr",
                    terminal=True)
                config.set('tor.key', '', savefile=True)
                return
        logger.info(
            f'{new_address}Tor transport address {add_onion_resp.service_id}' +
            '.onion',
            terminal=True)

