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
import locale, sys, os
locale.setlocale(locale.LC_ALL, '')
import onionrservices, logger
from onionrservices import bootstrapservice

plugin_name = 'clandestine'
PLUGIN_VERSION = '0.0.0'

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from . import controlapi, peerserver
flask_blueprint = controlapi.flask_blueprint
direct_blueprint = peerserver.direct_blueprint

def exit_with_error(text=''):
    if text != '':
        logger.error(text)
    sys.exit(1)

class Clandestine:
    def __init__(self, pluginapi):
        self.myCore = pluginapi.get_core()
    
    def create(self):
        try:
            peer = sys.argv[2]
            if not self.myCore._utils.validatePubKey(peer):
                exit_with_error('Invalid public key specified')
        except IndexError:
            exit_with_error('You must specify a peer public key')
        
        # Ask peer for transport address by creating block for them
        peer_transport_address = bootstrapservice.bootstrap_client_service(peer, self.myCore)

        print(peer_transport_address)
        if self.myCore._utils.doGetRequest('http://%s/ping' % (peer_transport_address,), ignoreAPI=True, port=self.myCore.config.get('tor.socksport')) == 'pong!':
            print('connected', peer_transport_address)

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    pluginapi = api
    chat = Clandestine(pluginapi)
    api.commands.register(['clandestine'], chat.create)
    return
