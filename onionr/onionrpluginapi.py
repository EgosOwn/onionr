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

import onionrplugins, logger, onionrcrypto
from onionrutils import localcommand
from coredb import daemonqueue
class DaemonAPI:
    def __init__(self, pluginapi):
        self.pluginapi = pluginapi

    def start(self):
        self.pluginapi.get_onionr().daemon()

        return

    def stop(self):
        self.pluginapi.get_onionr().killDaemon()

        return

    def queue(self, command, data = ''):
        return daemonqueue.daemon_queue_add(command, data)

    def local_command(self, command):
        return localcommand.local_command(command)

    def queue_pop(self):
        return daemonqueue.daemon_queue()

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
        events.event(name, data = data, onionr = self.pluginapi.get_onionr())

    def is_enabled(self, name):
        return onionrplugins.is_enabled(name)

    def get_enabled_plugins(self):
        return onionrplugins.get_enabled()

    def get_folder(self, name = None, absolute = True):
        return onionrplugins.get_plugins_folder(name = name, absolute = absolute)

    def get_data_folder(self, name, absolute = True):
        return onionrplugins.get_plugin_data_folder(name, absolute = absolute)

    def daemon_event(self, event, plugin = None):
        return # later make local command like /client/?action=makeEvent&event=eventname&module=modulename

class CommandAPI:
    def __init__(self, pluginapi):
        self.pluginapi = pluginapi

    def register(self, names, call = None):
        if isinstance(names, str):
            names = [names]

        for name in names:
            self.pluginapi.get_onionr().addCommand(name, call)

        return

    def unregister(self, names):
        if isinstance(names, str):
            names = [names]

        for name in names:
            self.pluginapi.get_onionr().delCommand(name)

        return

    def register_help(self, names, description):
        if isinstance(names, str):
            names = [names]

        for name in names:
            self.pluginapi.get_onionr().addHelp(name, description)

        return

    def unregister_help(self, names):
        if isinstance(names, str):
            names = [names]

        for name in names:
            self.pluginapi.get_onionr().delHelp(name)

        return

    def call(self, name):
        self.pluginapi.get_onionr().execute(name)

        return

    def get_commands(self):
        return self.pluginapi.get_onionr().getCommands()

class WebAPI:
    def __init__(self, pluginapi):
        self.pluginapi = pluginapi

    def register_callback(self, action, callback, scope = 'public'):
        return self.pluginapi.get_onionr().api.setCallback(action, callback, scope = scope)

    def unregister_callback(self, action, scope = 'public'):
        return self.pluginapi.get_onionr().api.removeCallback(action, scope = scope)

    def get_callback(self, action, scope = 'public'):
        return self.pluginapi.get_onionr().api.getCallback(action, scope=  scope)

    def get_callbacks(self, scope = None):
        return self.pluginapi.get_onionr().api.getCallbacks(scope = scope)

class pluginapi:
    def __init__(self, onionr, data):
        self.onionr = onionr
        self.data = data

        self.daemon = DaemonAPI(self)
        self.plugins = PluginAPI(self)
        self.commands = CommandAPI(self)
        self.web = WebAPI(self)
        self.crypto = onionrcrypto.OnionrCrypto()

    def get_onionr(self):
        return self.onionr

    def get_data(self):
        return self.data

    def get_crypto(self):
        return self.crypto

    def get_daemonapi(self):
        return self.daemon

    def get_pluginapi(self):
        return self.plugins

    def get_commandapi(self):
        return self.commands

    def get_webapi(self):
        return self.web

    def is_development_mode(self):
        return self.get_onionr()._developmentMode
