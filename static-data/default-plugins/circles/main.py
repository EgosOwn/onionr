"""Onionr - Private P2P Communication.

This default plugin handles "flow" messages
(global chatroom style communication)
"""
import sys
import os

import locale
locale.setlocale(locale.LC_ALL, '')

from blockio.subprocgenerate import gen_and_store_vdf_block

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# import after path insert
import flowapi  # noqa
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

flask_blueprint = flowapi.flask_blueprint
security_whitelist = ['circles.circlesstatic', 'circles.circlesindex']

plugin_name = 'circles'
PLUGIN_VERSION = '1.0.0'


def on_circles_cmd(api, data=None):
    message = ""
    while message != "-q":
        message = input("Enter message")
        gen_and_store_vdf_block()


