'''
    Onionr - Private P2P Communication

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
import os, re, importlib

from . import onionrevents as events
import config, logger
from utils import identifyhome

# set data dir
dataDir = identifyhome.identify_home()

_pluginsfolder = dataDir + 'plugins/'
_instances = dict()
config.reload()

def reload(stop_event = True):
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
                stop(plugin)

        for plugin in enabled_plugins:
            start(plugin)

        return True
    except:
        logger.error('Failed to reload plugins.')

    return False

def enable(name, start_event = True):
    '''
        Enables a plugin
    '''

    check()

    if exists(name):
        enabled_plugins = get_enabled_plugins()
        if not name in enabled_plugins:
            try:
                events.call(get_plugin(name), 'enable')
            except ImportError as e: # Was getting import error on Gitlab CI test "data"
                # NOTE: If you are experiencing issues with plugins not being enabled, it might be this resulting from an error in the module
                # can happen inconsistently (especially between versions)
                logger.debug('Failed to enable module; Import error: %s' % e)
                return False
            else:
                enabled_plugins.append(name)
                config.set('plugins.enabled', enabled_plugins, savefile=True)

                if start_event is True:
                    start(name)
                return True
        else:
            return False
    else:
        logger.error('Failed to enable plugin \"%s\", disabling plugin.' % name, terminal=True)
        logger.debug('Plugins folder not found: %s' % get_plugins_folder(str(name).lower()))
        disable(name)

        return False


def disable(name, stop_event = True):
    '''
        Disables a plugin
    '''

    check()

    if is_enabled(name):
        enabled_plugins = get_enabled_plugins()
        enabled_plugins.remove(name)
        config.set('plugins.enabled', enabled_plugins, True)

    if exists(name):
        events.call(get_plugin(name), 'disable')

        if stop_event is True:
            stop(name)

def start(name):
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
                events.call(plugin, 'start')

            return plugin
        except:
            logger.error('Failed to start module \"%s\".' % name)
    else:
        logger.error('Failed to start nonexistant module \"%s\".' % name)

    return None

def stop(name):
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
                events.call(plugin, 'stop')

            return plugin
        except:
            logger.error('Failed to stop module \"%s\".' % name)
    else:
        logger.error('Failed to stop nonexistant module \"%s\".' % name)

    return None

# credit: https://stackoverflow.com/a/29589414
def import_module_from_file(full_path_to_module):
    """
    Import a module given the full path/filename of the .py file

    Python 3.4

    """

    module = None

    # Get module name and path from full path
    module_dir, module_file = os.path.split(full_path_to_module)
    module_name, module_ext = os.path.splitext(module_file)

    module_name = module_dir # Module name must be unique otherwise it will get written in other imports

    # Get module "spec" from filename
    spec = importlib.util.spec_from_file_location(module_name,full_path_to_module)

    module = spec.loader.load_module()

    return module

def get_plugin(name):
    '''
        Returns the instance of a module
    '''

    check()

    if str(name).lower() in _instances:
        return _instances[str(name).lower()]
    else:
        _instances[str(name).lower()] = import_module_from_file(get_plugins_folder(str(name).lower(), False) + 'main.py')
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

    return list(config.get('plugins.enabled', list()))

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
        #path = _pluginsfolder + str(name.lower())
        path = _pluginsfolder + re.sub('[^0-9a-zA-Z_]+', '', str(name).lower())

    if absolute is True:
        path = os.path.abspath(path)

    return path + '/'

def get_plugin_data_folder(name, absolute = True):
    '''
        Returns the location of a plugin's data folder
    '''

    return get_plugins_folder(name, absolute)

def check():
    '''
        Checks to make sure files exist
    '''

    if not config.is_set('plugins'):
        logger.debug('Generating plugin configuration data...')
        config.set('plugins', {'enabled': []}, True)

    if not os.path.exists(os.path.dirname(get_plugins_folder())):
        logger.debug('Generating plugin data folder...')
        try:
            os.makedirs(os.path.dirname(get_plugins_folder()))
        except FileExistsError:
            pass
    return
