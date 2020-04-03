"""Onionr - Private P2P Communication.

This file deals with configuration management.
"""
import os
from json import JSONDecodeError

import ujson as json
import logger
import filepaths

from . import onboarding
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

_configfile = filepaths.config_file
_config = {}


def get(key, default = None, save = False):
    """Gets the key from configuration, or returns `default`"""

    key = str(key).split('.')
    data = _config

    last = key.pop()

    for item in key:
        if (not item in data) or (not type(data[item]) == dict):
            return default
        data = data[item]

    if last not in data:
        if save:
            set(key, default, savefile = True)
        return default

    return data[last]


def set(key, value = None, savefile = False):
    """Sets the key in configuration to `value`"""

    global _config

    whole_key = key
    key = str(key).split('.')
    data = _config

    last = key.pop()

    for item in key:
        if (not item in data) or (not type(data[item]) == dict):
            data[item] = dict()
        data = data[item]

    if value is None:
        del data[last]
    else:
        data[last] = value

    if savefile:
        save()


def is_set(key):
    key = str(key).split('.')
    data = _config

    last = key.pop()

    for item in key:
        if (not item in data) or (not type(data[item]) == dict):
            return False
        data = data[item]

    if not last in data:
        return False

    return True


def check():
    """Checks if the configuration file exists, creates it if not"""

    if not os.path.exists(os.path.dirname(get_config_file())):
        os.makedirs(os.path.dirname(get_config_file()))


def save():
    """Saves the configuration data to the configuration file"""

    check()
    try:
        with open(get_config_file(), 'w', encoding="utf8") as configfile:
            json.dump(get_config(), configfile, indent=2)
    except JSONDecodeError:
        logger.warn('Failed to write to configuration file.')


def reload():
    """Reloads the configuration data in memory from the file"""
    check()
    try:
        with open(get_config_file(), 'r', encoding="utf8") as configfile:
            set_config(json.loads(configfile.read()))
    except (FileNotFoundError, JSONDecodeError) as e:
        pass
        #logger.debug('Failed to parse configuration file.')


def get_config():
    """Gets the entire configuration as an array"""
    return _config


def set_config(config):
    """Sets the configuration to the array in arguments"""
    global _config
    _config = config


def get_config_file():
    """Returns the absolute path to the configuration file"""
    return _configfile


def set_config_file(configfile):
    """Sets the path to the configuration file."""
    global _configfile
    _configfile = os.abs.abspath(configfile)
