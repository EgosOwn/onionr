"""Onionr - Private P2P Communication.

This default plugin handles "flow" messages
(global chatroom style communication)
"""
import sys
import os
import locale
from typing import Set, TYPE_CHECKING
import base64

from stem.control import Controller

import logger
from utils import readstatic
import config
from filepaths import gossip_server_socket_file


from gossip.peer import Peer
import onionrcrypto

locale.setlocale(locale.LC_ALL, '')
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# import after path insert
import starttor
from torfilepaths import control_socket

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


def on_gossip_start(api, data: Set[Peer] = None):
    # We don't do gossip logic
    try:
        with open(bootstrap_file, 'r') as bootstrap_file_obj:
            bootstrap_nodes = bootstrap_file_obj.read().split(',')
    except FileNotFoundError:
        bootstrap_nodes = []
    #for node in bootstrap_nodes:
    starttor.start_tor()

    with Controller.from_socket_file(control_socket) as controller:
        controller.authenticate()
        logger.info(f"Tor socks is listening on {controller.get_listeners('SOCKS')}", terminal=True)
        key = config.get('tor.key')
        new_address = ''
        if not key:
            add_onion_resp = controller.create_ephemeral_hidden_service(
                {'80': f'unix:{gossip_server_socket_file}'},
                key_content='BEST', key_type='NEW')
            config.set('tor.key', add_onion_resp.private_key, savefile=True)
            new_address = 'Generated '
        else:
            add_onion_resp = controller.create_ephemeral_hidden_service(
                {'80': f'unix:{gossip_server_socket_file}'},
                key_content=key, key_type='ED25519-V3')
        logger.info(
            f'{new_address}Tor transport address {add_onion_resp.service_id}' +
            '.onion',
            terminal=True)

