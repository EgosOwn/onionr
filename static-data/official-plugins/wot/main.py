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


import logger

import onionrplugins

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
PLUGIN_VERSION = '0.0.0'
from wot.identity import identities
from wot.loadfromblocks import load_identities_from_blocks



def on_init(api, data=None):
    logger.info(
        f"Web of Trust Plugin v{PLUGIN_VERSION} enabled", terminal=True)
    #onionrplugins.plugin_apis['wot'] = wot_test

    list(map(lambda x: identities.add(x), load_identities_from_blocks()))