"""Onionr - Private P2P Communication.

Default example plugin for devs or to test blocks
"""
import sys
import os
import locale
from time import sleep
import traceback
from typing import Set, TYPE_CHECKING
from threading import Thread, local
import blockdb
from gossip.peerset import gossip_peer_set

import logger

import onionrblocks

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


plugin_name = 'example'
PLUGIN_VERSION = '0.0.0'


def on_blocktest_cmd(api, data=None):
    bl = onionrblocks.create_anonvdf_block(input("Enter a message:").encode('utf-8'), b"tst", 3600)


def on_printtest_cmd(api, data=None):
    while True:
        try:
            print(list(blockdb.get_blocks_by_type("tst"))[0].data)
        except IndexError:
            pass
        try:
            sleep(1)
        except KeyboardInterrupt:
            break



def on_init(api, data=None):
    logger.info(
        f"Example Plugin v{PLUGIN_VERSION} enabled", terminal=True)
