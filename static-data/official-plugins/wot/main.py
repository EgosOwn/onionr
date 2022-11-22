"""Onionr - Private P2P Communication.

Web of Trust Plugin
"""
import sys
import os
import locale
from time import sleep
from typing import Set, TYPE_CHECKING
from threading import Thread, local

from gossip.peerset import gossip_peer_set
from logger import log as logging
import config
import onionrplugins
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
from wot.identity import identities
from wot import wotkeyring
from cli import main_ui
from onionrplugins import plugin_apis

import wot
from wot.loadfromblocks import load_identities_from_blocks


def on_init(api, data=None):
    def load_identity_from_config(identity_name: str):
        identity_base85_key = config.get('wot.identity.{identity_name}')

    logging.info(
        f"Web of Trust Plugin v{PLUGIN_VERSION} enabled")

    list(
        map(
            lambda x: identities.add(x),
            load_identities_from_blocks())
        )

    plugin_apis['rpc.add_module_to_api'](wot)

    # load active identity, from there load our trust graph
    active_identity = config.get('wot.active_identity_name', '')
    if not active_identity:
        try:
            script = sys.argv[0] + ' '
        except IndexError:
            script = ''
        logging.info(
            f"Generate a web of trust identity with '{script}wot new" +
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



def on_wot_cmd(api, data=None):
    main_ui()
