'''
    Onionr - P2P Anonymous Storage Network

    Instant message conversations with Onionr peers
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
import locale

locale.setlocale(locale.LC_ALL, '')

plugin_name = 'clandenstine'
PLUGIN_VERSION = '0.0.0'

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from . import controlapi
flask_blueprint = controlapi.flask_blueprint

class Clandenstine:
    def __init__(self, pluginapi):
        self.myCore = pluginapi.get_core()

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    pluginapi = api
    chat = Clandenstine(pluginapi)
    return
