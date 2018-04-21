'''
    Onionr - P2P Microblogging Platform & Social network

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

import onionrplugins as plugins, logger

class PluginAPI:
    def __init__(self, onionr):
        self.onionr = onionr
        
        self.daemon = DaemonAPI(self)
        self.plugin = PluginAPI(self)
        self.command = CommandAPI(self)
        
    def get_onionr(self):
        return self.onionr
        
    def get_core(self):
        return self.get_onionr().onionrCore
        
    def get_utils(self):
        return self.get_onionr().onionrUtils
        
    def get_daemonapi(self):
        return self.daemon
        
    def get_pluginapi(self):
        return self.plugin
    
    def get_commandapi(self):
        return self.command
        
    def is_development_mode(self):
        return self.get_onionr()._developmentMode

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
            self.pluginapi.get_core().daemonQueueAdd(command, data)
            
            return
            
        def local_command(self, command):
            self.pluginapi.get_utils().localCommand(self, command)
            
            return
            
        def queue_pop(self):
            return self.get_core().daemonQueue()
        
    class PluginAPI:
        def __init__(self, pluginapi):
            self.pluginapi = pluginapi
        
        def start(self, name):
            plugins.start(name)

        def stop(self, name):
            plugins.stop(name)

        def reload(self, name):
            plugins.reload(name)

        def enable(self, name):
            plugins.enable(name)

        def disable(self, name):
            plugins.disable(name)

        def is_enabled(self, name):
            return plugins.is_enabled(name)

        def get_enabled_plugins(self):
            return plugins.get_enabled_plugins()

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
