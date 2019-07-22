'''
    Onionr - Private P2P Communication

    Initialize Onionr configuration
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
import os, json
import config, logger
from logger.settings import *

def setup_config(dataDir, o_inst = None):
    data_exists = os.path.exists(dataDir)
    if not data_exists:
        os.mkdir(dataDir)
    config.reload()
    
    if not os.path.exists(config._configfile):
        if os.path.exists('static-data/default_config.json'):
            # this is the default config, it will be overwritten if a config file already exists. Else, it saves it
            with open('static-data/default_config.json', 'r') as configReadIn:
                config.set_config(json.loads(configReadIn.read()))
        else:
            # the default config file doesn't exist, try hardcoded config
            logger.warn('Default configuration file does not exist, switching to hardcoded fallback configuration!')
            config.set_config({'dev_mode': True, 'log': {'file': {'output': True, 'path': dataDir + 'output.log'}, 'console': {'output': True, 'color': True}}})

        config.save()

    settings = 0b000
    if config.get('log.console.color', True):
        settings = settings | USE_ANSI
    if config.get('log.console.output', True):
        settings = settings | OUTPUT_TO_CONSOLE
    if config.get('log.file.output', True):
        settings = settings | OUTPUT_TO_FILE
    set_settings(settings)

    if not o_inst is None:
        if str(config.get('general.dev_mode', True)).lower() == 'true':
            o_inst._developmentMode = True
            set_level(LEVEL_DEBUG)
        else:
            o_inst._developmentMode = False
            set_level(LEVEL_INFO)

    verbosity = str(config.get('log.verbosity', 'default')).lower().strip()
    if not verbosity in ['default', 'null', 'none', 'nil']:
        map = {
            str(LEVEL_DEBUG) : LEVEL_DEBUG,
            'verbose' : LEVEL_DEBUG,
            'debug' : LEVEL_DEBUG,
            str(LEVEL_INFO) : LEVEL_INFO,
            'info' : LEVEL_INFO,
            'information' : LEVEL_INFO,
            str(LEVEL_WARN) : LEVEL_WARN,
            'warn' : LEVEL_WARN,
            'warning' : LEVEL_WARN,
            'warnings' : LEVEL_WARN,
            str(LEVEL_ERROR) : LEVEL_ERROR,
            'err' : LEVEL_ERROR,
            'error' : LEVEL_ERROR,
            'errors' : LEVEL_ERROR,
            str(LEVEL_FATAL) : LEVEL_FATAL,
            'fatal' : LEVEL_FATAL,
            str(LEVEL_IMPORTANT) : LEVEL_IMPORTANT,
            'silent' : LEVEL_IMPORTANT,
            'quiet' : LEVEL_IMPORTANT,
            'important' : LEVEL_IMPORTANT
        }

        if verbosity in map:
            set_level(map[verbosity])
        else:
            logger.warn('Verbosity level %s is not valid, using default verbosity.' % verbosity)

    return data_exists