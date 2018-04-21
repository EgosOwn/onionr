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

import config, logger, onionrplugins as plugins, onionrpluginapi as pluginapi

def get_pluginapi(onionr, data):
    return pluginapi.pluginapi(onionr, data)

def event(event_name, data = {}, onionr = None):
    '''
        Calls an event on all plugins (if defined)
    '''

    for plugin in plugins.get_enabled_plugins():
        try:
            call(plugins.get_plugin(plugin), event_name, data, get_pluginapi(onionr, data))
        except Exception as e:
            logger.warn('Event \"' + event_name + '\" failed for plugin \"' + plugin + '\".')
            logger.debug(str(e))

def call(plugin, event_name, data = None, pluginapi = None):
    '''
        Calls an event on a plugin if one is defined
    '''

    if not plugin is None:
        try:
            attribute = 'on_' + str(event_name).lower()

            # TODO: Use multithreading perhaps?
            if hasattr(plugin, attribute):
                #logger.debug('Calling event ' + str(event_name))
                getattr(plugin, attribute)(pluginapi)

            return True
        except Exception as e:
            logger.debug(str(e))
            return False
    else:
        return True
