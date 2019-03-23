'''
    Onionr - P2P Anonymous Storage Network

    Bootstrap onion direct connections for the clients
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
from gevent.pywsgi import WSGIServer, WSGIHandler
from stem.control import Controller
from flask import Flask
import core
from netcontroller import getOpenPort        

def bootstrap_client_service(peer, core_inst=None, bootstrap_timeout=300):
    '''
        Bootstrap client services
    '''
    if core_inst is None:
        core_inst = core.Core()
    
    if not core_inst._utils.validatePubKey(peer):
        raise ValueError('Peer must be valid base32 ed25519 public key')

    bootstrap_port = getOpenPort()
    bootstrap_app = Flask(__name__)
    http_server = WSGIServer(('127.0.0.1', bootstrap_port), bootstrap_app, log=None)
    
    bootstrap_address = ''

    @bootstrap_app.route('/ping')
    def get_ping():
        return "pong!"

    @bootstrap_app.route('/bs/<address>', methods=['POST'])
    def get_bootstrap(address):
        if core_inst._utils.validateID(address):
            # Set the bootstrap address then close the server
            bootstrap_address = address
            http_server.stop()

    with Controller.from_port(port=core_inst.config.get('tor.controlPort')) as controller:
        # Connect to the Tor process for Onionr
        controller.authenticate(core_inst.config.get('tor.controlpassword'))
        # Create the v3 onion service
        #response = controller.create_ephemeral_hidden_service({80: bootstrap_port}, await_publication = True, key_content = 'ED25519-V3')
        response = controller.create_ephemeral_hidden_service(80, key_type = 'NEW', await_publication = True)

        core_inst.insertBlock(response.service_id, header='con', sign=True, encryptType='asym', 
        asymPeer=peer, disableForward=True, expire=(core_inst._utils.getEpoch() + bootstrap_timeout))
        
        # Run the bootstrap server
        http_server.serve_forever()
        # This line reached when server is shutdown by being bootstrapped
    
    # Now that the bootstrap server has received a server, return the address
    return bootstrap_address
