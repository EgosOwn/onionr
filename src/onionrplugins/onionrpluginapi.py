'''
    Onionr - Private P2P Communication

    This file deals with the object that is passed with each event
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

import onionrplugins, logger
from onionrutils import localcommand

class PluginAPI:
    def __init__(self, pluginapi):
        self.pluginapi = pluginapi

    def start(self, name):
        onionrplugins.start(name)

    def stop(self, name):
        onionrplugins.stop(name)

    def reload(self, name):
        onionrplugins.reload(name)

    def enable(self, name):
        onionrplugins.enable(name)

    def disable(self, name):
        onionrplugins.disable(name)

    def event(self, name, data = {}):
        events.event(name, data = data)

    def is_enabled(self, name):
        return onionrplugins.is_enabled(name)

    def get_enabled_plugins(self):
        return onionrplugins.get_enabled()

    def get_folder(self, name = None, absolute = True):
        return onionrplugins.get_plugins_folder(name = name, absolute = absolute)

    def get_data_folder(self, name, absolute = True):
        return onionrplugins.get_plugin_data_folder(name, absolute = absolute)

class CommandAPI:
    def __init__(self, pluginapi):
        self.pluginapi = pluginapi

    def call(self, name):
        self.pluginapi.get_onionr().execute(name)

class SharedAPI:
    def __init__(self, data):
        self.data = data
        self.plugins = PluginAPI(self)

    def get_data(self):
        return self.data

    def get_daemonapi(self):
        return self.daemon

    def get_pluginapi(self):
        return self.plugins