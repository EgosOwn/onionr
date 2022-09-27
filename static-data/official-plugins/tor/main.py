"""Onionr - Private P2P Communication.

Tor transport plugin
"""
import sys
import os
import locale
from time import sleep
import traceback
from typing import Set, TYPE_CHECKING
import base64
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
import starttor
from torpeer import TorPeer
from torfilepaths import control_socket

from bootstrap import on_bootstrap
from announce import on_announce_rec
from shutdown import on_shutdown_event

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


class OnionrTor:
    def __init__(self):
        return


def on_init(api, data=None):
    logger.info(
        f"Tor Transport Plugin v{PLUGIN_VERSION} enabled", terminal=True)


def on_get_our_transport(api, data=None):
    callback_func = data['callback']
    for_peer = data['peer']
    if data['peer'].__class__ == TorPeer:
        callback_func(for_peer, config.get('tor.transport_address'))


def on_gossip_start(api, data: Set[Peer] = None):
    # We don't do gossip logic

    starttor.start_tor()

    with Controller.from_socket_file(control_socket) as controller:
        controller.authenticate()
        logger.info(
            "Tor socks is listening on " +
            f"{controller.get_listeners('SOCKS')[0]}", terminal=True)
        key = config.get('tor.key')
        new_address = ''
        if not key:
            add_onion_resp = controller.create_ephemeral_hidden_service(
                {'80': f'unix:{gossip_server_socket_file}'},
                key_content='BEST', key_type='NEW', detached=True)
            config.set('tor.key', add_onion_resp.private_key, savefile=True)
            new_address = 'Generated '
            onion = add_onion_resp.service_id
            onion = onion.removesuffix('.onion') + '.onion'
            config.set('tor.transport_address', onion,
            savefile=True)
        else:
            try:
                add_onion_resp = controller.create_ephemeral_hidden_service(
                    {'80': f'unix:{gossip_server_socket_file}'},
                    key_content=key, key_type='ED25519-V3',
                    detached=True, await_publication=True)
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