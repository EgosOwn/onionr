'''
    Onionr - Private P2P Communication

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
import locale, sys, os, threading, json
locale.setlocale(locale.LC_ALL, '')
import onionrservices, logger
from onionrservices import bootstrapservice

plugin_name = 'esoteric'
PLUGIN_VERSION = '0.0.0'
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import controlapi, peerserver
flask_blueprint = controlapi.flask_blueprint
direct_blueprint = peerserver.direct_blueprint

def exit_with_error(text=''):
    if text != '':
        logger.error(text)
    sys.exit(1)

class Esoteric:
    def __init__(self, pluginapi):
        self.myCore = pluginapi.get_core()
        self.peer = None
        self.transport = None
        self.shutdown = False
    
    def _sender_loop(self):
        print('Enter a message to send, with ctrl-d or -s on a new line.')
        print('-c on a new line or ctrl-c stops')
        message = ''
        while not self.shutdown:
            try:
                message += input()
                if message == '-s':
                    raise EOFError
                elif message == '-c':
                    raise KeyboardInterrupt
                else:
                    message += '\n'
            except EOFError:
                message = json.dumps({'m': message, 't': self.myCore._utils.getEpoch()})
                print(self.myCore._utils.doPostRequest('http://%s/esoteric/sendto' % (self.transport,), port=self.socks, data=message))
                message = ''
            except KeyboardInterrupt:
                self.shutdown = True

    def create(self):
        try:
            peer = sys.argv[2]
            if not self.myCore._utils.validatePubKey(peer):
                exit_with_error('Invalid public key specified')
        except IndexError:
            exit_with_error('You must specify a peer public key')
        self.peer = peer
        # Ask peer for transport address by creating block for them
        peer_transport_address = bootstrapservice.bootstrap_client_service(peer, self.myCore)
        self.transport = peer_transport_address
        self.socks = self.myCore.config.get('tor.socksport')

        print('connected with', peer, 'on', peer_transport_address)
        if self.myCore._utils.doGetRequest('http://%s/ping' % (peer_transport_address,), ignoreAPI=True, port=self.socks) == 'pong!':
            print('connected', peer_transport_address)
            threading.Thread(target=self._sender_loop).start()

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    pluginapi = api
    chat = Esoteric(pluginapi)
    api.commands.register(['esoteric'], chat.create)
    return
