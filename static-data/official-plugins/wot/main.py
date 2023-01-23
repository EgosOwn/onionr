"""Onionr - Private P2P Communication.

Web of Trust Plugin
"""
import sys
import os
import base64
import locale
from time import sleep
import traceback
from typing import Set, TYPE_CHECKING

import keyring.errors
from nacl.signing import SigningKey

from gossip.peerset import gossip_peer_set
from logger import log as logging
import config
from onionrplugins.pluginapis import plugin_apis

locale.setlocale(locale.LC_ALL, '')
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# import after path insert

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
plugin_name = 'wot'
PLUGIN_VERSION = '0.0.1'
from wot.identity import Identity, identities
from wot import wotkeyring
from cli import main_ui
from onionrplugins import plugin_apis

import wot
from wot.loadfromblocks import load_identities_from_blocks


def on_init(api, data=None):
    def load_identity_from_config(identity_name: str):
        identity_base85_key = config.get('wot.identity.{identity_name}', '')
        if not identity_base85_key:
            raise KeyError('Identity not found in config')
        key = SigningKey(base64.base85decode(identity_base85_key))
        identity = identities.Identity(identity_name, key)
        return identity


    logging.info(
        f"Web of Trust Plugin v{PLUGIN_VERSION} enabled")

    list(
        map(
            lambda x: identities.add(x),
            load_identities_from_blocks())
        )

    # Expose WOT to RPC if the RPC plugin is loaded
    try:
        plugin_apis['rpc.add_module_to_api'](wot)
    except KeyError:
        pass

    # load active identity, from there load our trust graph
    active_identity = config.get('wot.active_identity_name', '')
    if not active_identity:
        try:
            script = sys.argv[0] + ' '
        except IndexError:
            script = ''
        logging.info(
            f"Generate a web of trust identity with '{script}wot new " +
            "<name>' and restart Onionr")
        return

    if config.get('wot.use_system_keyring', True):
        try:
            iden = wotkeyring.get_identity_by_name(active_identity)
        except KeyError:
            logging.error(
                f"Could not load identity {active_identity} " +
                "from keyring despite configuration choice to do so")
    else:
        # load from file
        iden = load_identity_from_config(active_identity)

        try:
            iden = wotkeyring.get_identity_by_name(active_identity)
        except KeyError:
            logging.error(
                "Active identity's private key not found in config or keyring")
            return

    logging.info('Loaded active identity: ' + iden.name)
    identities.add(iden)


def on_wot_cmd(api, data=None):
    def _create_new_iden():
        iden = Identity(
            SigningKey.generate(),
            input('Enter a name for your identity: '))
        try:
            wotkeyring.set_identity(iden)
        except keyring.errors.NoKeyringError:
            logging.warn(
                "Could not use secure keyring to store your WOT " +
                "private key, using config.")
            logging.info("Using config file to store identity private key")
            config.set(
                'wot.identity.{iden.name}',
                base64.b85encode(
                    bytes(iden.private_key)).decode('utf-8'), savefile=True)
        config.set(
            'wot.active_identity_name', iden.name, savefile=True)
        logging.info(
            'Identity created and automatically set as active. ' +
            'Restart Onionr to use it.')
    try:
        cmd = sys.argv[2]
    except IndexError:
        cmd = ''

    match cmd:
        case 'new':
            try:
                _create_new_iden()
            except KeyboardInterrupt:
                pass
        case '':
            main_ui()
