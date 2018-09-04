'''
    Onionr - P2P Anonymous Storage Network

    This is an interactive menu-driven CLI interface for Onionr
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

# Imports some useful libraries
import logger, config, sys
from onionrblockapi import Block
try:
    import tkinter
except (ModuleNotFoundError, ImportError, NameError) as e:
    TK_ENABLED = False
else:
    TK_ENABLED = True


plugin_name = 'cliui'
PLUGIN_VERSION = '0.0.1'

class OnionrBoards:
    def __init__(self, apiInst):
        self.api = apiInst
        self.myCore = apiInst.get_core()

        self.gui = tkinter.Tk()

        return

    def start(self):
        return

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    # Doing this makes it so that the other functions can access the api object
    # by simply referencing the variable `pluginapi`.
    pluginapi = api
    ui = OnionrBoards(api)
    api.commands.register('boards', ui.start)
    api.commands.register_help('boards', 'Open the board viewer')


    return
