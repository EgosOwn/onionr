'''
    Onionr - P2P Microblogging Platform & Social network

    This default plugin handles "flow" messages (global chatroom style communication)
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
import logger, config
from onionrblockapi import Block

plugin_name = 'flow'

class OnionrFlow:
    def __init__(self):
        logger.info("HELLO")
        return



def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    # Doing this makes it so that the other functions can access the api object
    # by simply referencing the variable `pluginapi`.
    global pluginapi
    pluginapi = api
    api.commands.register(['flow'], OnionrFlow)
    api.commands.register_help('flow', 'Open the flow messaging interface')
    return