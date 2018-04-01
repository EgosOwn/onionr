'''
    Onionr - P2P Microblogging Platform & Social network

    This file deals with configuration management.
'''
'''
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
'''

import os, json, logger

_configfile = os.path.abspath('data/config.json')
_config = {}

def get(key, default = None):
    '''
        Gets the key from configuration, or returns `default`
    '''

    if is_set(key):
        return get_config()[key]
    return default

def set(key, value = None, savefile = False):
    '''
        Sets the key in configuration to `value`
    '''

    global _config
    if value is None:
        del _config[key]
    else:
        _config[key] = value

    if savefile:
        save()

def is_set(key):
    return key in get_config() and not get_config()[key] is None

def check():
    '''
        Checks if the configuration file exists, creates it if not
    '''

    try:
        if not os.path.exists(os.path.dirname(get_config_file())):
            os.path.mkdirs(os.path.dirname(get_config_file()))
        if not os.path.isfile(get_config_file()):
            open(get_config_file(), 'a', encoding="utf8").close()
            save()
    except:
        logger.warn('Failed to check configuration file.')

def save():
    '''
        Saves the configuration data to the configuration file
    '''

    check()
    try:
        with open(get_config_file(), 'w', encoding="utf8") as configfile:
            json.dump(get_config(), configfile, indent=2, sort_keys=True)
    except:
        logger.warn('Failed to write to configuration file.')

def reload():
    '''
        Reloads the configuration data in memory from the file
    '''

    check()
    try:
        with open(get_config_file(), 'r', encoding="utf8") as configfile:
            set_config(json.loads(configfile.read()))
    except:
        logger.warn('Failed to parse configuration file.')

def get_config():
    '''
        Gets the entire configuration as an array
    '''
    return _config

def set_config(config):
    '''
        Sets the configuration to the array in arguments
    '''
    global _config
    _config = config

def get_config_file():
    '''
        Returns the absolute path to the configuration file
    '''
    return _configfile

def set_config_file(configfile):
    '''
        Sets the path to the configuration file
    '''
    global _configfile
    _configfile = os.abs.abspath(configfile)
