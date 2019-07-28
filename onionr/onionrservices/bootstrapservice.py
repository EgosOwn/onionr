'''
    Onionr - Private P2P Communication

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
import time, threading, uuid
from gevent.pywsgi import WSGIServer, WSGIHandler
from stem.control import Controller
from flask import Flask, Response
from netcontroller import get_open_port
from . import httpheaders
from onionrutils import stringvalidators, epoch
import config, onionrblocks
def bootstrap_client_service(peer, onionr_inst=None, bootstrap_timeout=300):
    '''
        Bootstrap client services
    '''
    
    if not stringvalidators.validate_pub_key(peer):
        raise ValueError('Peer must be valid base32 ed25519 public key')

    bootstrap_port = get_open_port()
    bootstrap_app = Flask(__name__)
    http_server = WSGIServer(('127.0.0.1', bootstrap_port), bootstrap_app, log=None)
    try:
        assert onionr_inst.communicatorInst is not None
    except (AttributeError, AssertionError) as e:
        pass
    else:
        onionr_inst.communicatorInst.service_greenlets.append(http_server)
    
    bootstrap_address = ''
    shutdown = False
    bs_id = str(uuid.uuid4())

    @bootstrap_app.route('/ping')
    def get_ping():
        return "pong!"

    @bootstrap_app.after_request
    def afterReq(resp):
        # Security headers
        resp = httpheaders.set_default_onionr_http_headers(resp)
        return resp

    @bootstrap_app.route('/bs/<address>', methods=['POST'])
    def get_bootstrap(address):
        if stringvalidators.validate_transport(address + '.onion'):
            # Set the bootstrap address then close the server
            bootstrap_address = address + '.onion'
            core_inst.keyStore.put(bs_id, bootstrap_address)
            http_server.stop()
            return Response("success")
        else:
            return Response("")

    with Controller.from_port(port=config.get('tor.controlPort')) as controller:
        # Connect to the Tor process for Onionr
        controller.authenticate(config.get('tor.controlpassword'))
        # Create the v3 onion service
        response = controller.create_ephemeral_hidden_service({80: bootstrap_port}, key_type = 'NEW', key_content = 'ED25519-V3', await_publication = True)
        onionrblocks.insert(response.service_id, header='con', sign=True, encryptType='asym', 
        asymPeer=peer, disableForward=True, expire=(epoch.get_epoch() + bootstrap_timeout))
        # Run the bootstrap server
        try:
            http_server.serve_forever()
        except TypeError:
            pass
        # This line reached when server is shutdown by being bootstrapped
    
    # Now that the bootstrap server has received a server, return the address
    return onionr_inst.keyStore.get(bs_id)
