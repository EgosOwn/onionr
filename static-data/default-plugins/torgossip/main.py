"""
Onionr - Private P2P Communication

Default plugin which allows users to encrypt/decrypt messages w/o using blocks
"""
from inspect import trace
import locale
locale.setlocale(locale.LC_ALL, '')
import sys
import os
import traceback
from threading import Thread
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
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
plugin_name = 'torgossip'

import logger  # noqa

try:
    from server import start_server
    from peerdb import TorGossipPeers
    from runtest import torgossip_runtest
except Exception as _:  # noqa
    logger.error(traceback.format_exc(), terminal=True)


def on_init(api, data=None):
    shared_state = data
    shared_state.get_by_string(
        "OnionrRunTestManager").plugin_tests.append(torgossip_runtest)

    shared_state.get(TorGossipPeers)

    Thread(target=start_server, daemon=True, args=[shared_state]).start()

