"""
Onionr - Private P2P Communication

This default plugin allows users to encrypt/decrypt messages without using blocks
"""
import locale
locale.setlocale(locale.LC_ALL, '')
import sys
import os
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
from server import start_server


def on_init(api, data=None):
    print("starting gossip transport")
    Thread(target=start_server, daemon=True).start()

