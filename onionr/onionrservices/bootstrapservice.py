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
import time, threading, uuid, os
from gevent.pywsgi import WSGIServer, WSGIHandler
from stem.control import Controller
from flask import Flask, Response
from netcontroller import get_open_port
from . import httpheaders
from onionrutils import stringvalidators, epoch
import logger
import config, onionrblocks, filepaths
import onionrexceptions
import deadsimplekv as simplekv
from . import pool

def __bootstrap_timeout(server: WSGIServer, timeout: int, signal_object):
    time.sleep(timeout)
    signal_object.timed_out = True
    server.stop()

def bootstrap_client_service(peer, comm_inst=None, bootstrap_timeout=300):
    '''
        Bootstrap client services
    '''
    if not stringvalidators.validate_pub_key(peer):
        raise ValueError('Peer must be valid base32 ed25519 public key')
    
    connection_pool = None

    # here we use a lambda for the timeout thread to set to true
    timed_out = lambda: None
    timed_out.timed_out = False

    bootstrap_port = get_open_port()
    bootstrap_app = Flask(__name__)
    bootstrap_app.config['MAX_CONTENT_LENGTH'] = 1 * 1024

    http_server = WSGIServer(('127.0.0.1', bootstrap_port), bootstrap_app, log=None)
    try:
        assert comm_inst is not None
    except (AttributeError, AssertionError) as e:
        pass
    else:
        comm_inst.service_greenlets.append(http_server)
        connection_pool = comm_inst.shared_state.get(pool.ServicePool)
    
    bootstrap_address = ''
    shutdown = False
    bs_id = str(uuid.uuid4())
    key_store = simplekv.DeadSimpleKV(filepaths.cached_storage)

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
            key_store.put(bs_id, bootstrap_address)
            http_server.stop()
            return Response("success")
        else:
            return Response("")

    with Controller.from_port(port=config.get('tor.controlPort')) as controller:
        if not connection_pool is None: connection_pool.bootstrap_pending.append(peer)
        # Connect to the Tor process for Onionr
        controller.authenticate(config.get('tor.controlpassword'))
        # Create the v3 onion service
        response = controller.create_ephemeral_hidden_service({80: bootstrap_port}, key_type = 'NEW', key_content = 'ED25519-V3', await_publication = True)
        onionrblocks.insert(response.service_id, header='con', sign=True, encryptType='asym', 
        asymPeer=peer, disableForward=True, expire=(epoch.get_epoch() + bootstrap_timeout))
        
        threading.Thread(target=__bootstrap_timeout, args=[http_server, bootstrap_timeout, timed_out], daemon=True).start()

        # Run the bootstrap server
        try:
            http_server.serve_forever()
        except TypeError:
            pass
        # This line reached when server is shutdown by being bootstrapped
    # Add the address to the client pool
    if not comm_inst is None:
        connection_pool.bootstrap_pending.remove(peer)
        if timed_out.timed_out:
            logger.warn('Could not connect to %s due to timeout' % (peer,))
            return None
        comm_inst.direct_connection_clients[peer] = response.service_id

    # Now that the bootstrap server has received a server, return the address
    return key_store.get(bs_id)
