"""Onionr - Private P2P Communication.

Initialize Onionr configuration
"""
import os
import base64

import ujson as json

import config
from logger import log as logging
import onionrvalues
from utils import readstatic
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


def setup_config():
    if not os.path.exists(config._configfile):
        # this is the default config, it will be overwritten if a config file already exists. Else, it saves it
        conf_data = readstatic.read_static('default_config.json', ret_bin=False)
        config.set_config(json.loads(conf_data))

        config.save()

    config.reload()
