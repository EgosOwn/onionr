'''
    Onionr - P2P Microblogging Platform & Social network

    This file deals with management of modules/plugins.
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

import os, re, importlib, config, logger
import onionrevents as events

_pluginsfolder = 'data/plugins/'
_instances = dict()

def reload(onionr = None, stop_event = True):
    '''
        Reloads all the plugins
    '''

    check()

    try:
        enabled_plugins = get_enabled_plugins()

        if stop_event is True:
            logger.debug('Reloading all plugins...')
        else:
            logger.debug('Loading all plugins...')

        if stop_event is True:
            for plugin in enabled_plugins:
                stop(plugin, onionr)

        for plugin in enabled_plugins:
            start(plugin, onionr)

        return True
    except:
        logger.error('Failed to reload plugins.')

    return False


def enable(name, onionr = None, start_event = True):
    '''
        Enables a plugin
    '''

    check()

    if exists(name):
        enabled_plugins = get_enabled_plugins()
        if not name in enabled_plugins:
            enabled_plugins.append(name)
            config.set('plugins.enabled', enabled_plugins, True)

            events.call(get_plugin(name), 'enable', onionr)

            if start_event is True:
                start(name)

            return True
        else:
            return False
    else:
        logger.error('Failed to enable plugin \"%s\", disabling plugin.' % name)
        disable(name)

        return False


def disable(name, onionr = None, stop_event = True):
    '''
        Disables a plugin
    '''

    check()

    if is_enabled(name):
        enabled_plugins = get_enabled_plugins()
        enabled_plugins.remove(name)
        config.set('plugins.enabled', enabled_plugins, True)

    if exists(name):
        events.call(get_plugin(name), 'disable', onionr)

        if stop_event is True:
            stop(name)

def start(name, onionr = None):
    '''
        Starts the plugin
    '''

    check()

    if exists(name):
        try:
            plugin = get_plugin(name)

            if plugin is None:
                raise Exception('Failed to import module.')
            else:
                events.call(plugin, 'start', onionr)

            return plugin
        except:
            logger.error('Failed to start module \"%s\".' % name)
    else:
        logger.error('Failed to start nonexistant module \"%s\".' % name)

    return None

def stop(name, onionr = None):
    '''
        Stops the plugin
    '''

    check()

    if exists(name):
        try:
            plugin = get_plugin(name)

            if plugin is None:
                raise Exception('Failed to import module.')
            else:
                events.call(plugin, 'stop', onionr)

            return plugin
        except:
            logger.error('Failed to stop module \"%s\".' % name)
    else:
        logger.error('Failed to stop nonexistant module \"%s\".' % name)

    return None

def get_plugin(name):
    '''
        Returns the instance of a module
    '''

    check()

    if str(name).lower() in _instances:
        return _instances[str(name).lower()]
    else:
        _instances[str(name).lower()] = importlib.import_module(get_plugins_folder(name, False).replace('/', '.') + 'main')
        return get_plugin(name)

def get_plugins():
    '''
        Returns a list of plugins (deprecated)
    '''

    return _instances

def exists(name):
    '''
        Return value indicates whether or not the plugin exists
    '''

    return os.path.isdir(get_plugins_folder(str(name).lower()))

def get_enabled_plugins():
    '''
        Returns a list of the enabled plugins
    '''

    check()

    config.reload()

    return config.get('plugins.enabled', list())

def is_enabled(name):
    '''
        Return value indicates whether or not the plugin is enabled
    '''

    return name in get_enabled_plugins()

def get_plugins_folder(name = None, absolute = True):
    '''
        Returns the path to the plugins folder
    '''

    path = ''

    if name is None:
        path = _pluginsfolder
    else:
        # only allow alphanumeric characters
        path = _pluginsfolder + re.sub('[^0-9a-zA-Z]+', '', str(name).lower())

    if absolute is True:
        path = os.path.abspath(path)

    return path + '/'

def get_plugin_data_folder(name, absolute = True):
    '''
        Returns the location of a plugin's data folder
    '''

    return get_plugins_folder(name, absolute) + 'data/'

def check():
    '''
        Checks to make sure files exist
    '''

    config.reload()

    if not config.is_set('plugins'):
        logger.debug('Generating plugin config data...')
        config.set('plugins', {'enabled': []}, True)

    if not os.path.exists(os.path.dirname(get_plugins_folder())):
        logger.debug('Generating plugin data folder...')
        os.makedirs(os.path.dirname(get_plugins_folder()))

    return
