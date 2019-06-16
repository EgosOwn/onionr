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
        settings = settings | logger.USE_ANSI
    if config.get('log.console.output', True):
        settings = settings | logger.OUTPUT_TO_CONSOLE
    if config.get('log.file.output', True):
        settings = settings | logger.OUTPUT_TO_FILE
    logger.set_settings(settings)

    if not o_inst is None:
        if str(config.get('general.dev_mode', True)).lower() == 'true':
            o_inst._developmentMode = True
            logger.set_level(logger.LEVEL_DEBUG)
        else:
            o_inst._developmentMode = False
            logger.set_level(logger.LEVEL_INFO)

    verbosity = str(config.get('log.verbosity', 'default')).lower().strip()
    if not verbosity in ['default', 'null', 'none', 'nil']:
        map = {
            str(logger.LEVEL_DEBUG) : logger.LEVEL_DEBUG,
            'verbose' : logger.LEVEL_DEBUG,
            'debug' : logger.LEVEL_DEBUG,
            str(logger.LEVEL_INFO) : logger.LEVEL_INFO,
            'info' : logger.LEVEL_INFO,
            'information' : logger.LEVEL_INFO,
            str(logger.LEVEL_WARN) : logger.LEVEL_WARN,
            'warn' : logger.LEVEL_WARN,
            'warning' : logger.LEVEL_WARN,
            'warnings' : logger.LEVEL_WARN,
            str(logger.LEVEL_ERROR) : logger.LEVEL_ERROR,
            'err' : logger.LEVEL_ERROR,
            'error' : logger.LEVEL_ERROR,
            'errors' : logger.LEVEL_ERROR,
            str(logger.LEVEL_FATAL) : logger.LEVEL_FATAL,
            'fatal' : logger.LEVEL_FATAL,
            str(logger.LEVEL_IMPORTANT) : logger.LEVEL_IMPORTANT,
            'silent' : logger.LEVEL_IMPORTANT,
            'quiet' : logger.LEVEL_IMPORTANT,
            'important' : logger.LEVEL_IMPORTANT
        }

        if verbosity in map:
            logger.set_level(map[verbosity])
        else:
            logger.warn('Verbosity level %s is not valid, using default verbosity.' % verbosity)

    return data_exists