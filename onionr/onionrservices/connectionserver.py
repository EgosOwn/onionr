'''
    Onionr - Private P2P Communication

    This module does the second part of the bootstrap block handshake and creates the API server
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
from gevent.pywsgi import WSGIServer
from stem.control import Controller
from flask import Flask
import logger, httpapi
import onionrexceptions, config
from netcontroller import get_open_port
from httpapi import apiutils
from onionrutils import stringvalidators, basicrequests, bytesconverter
from . import httpheaders

class ConnectionServer:
    def __init__(self, peer, address, comm_inst=None):

        if not stringvalidators.validate_pub_key(peer):
            raise ValueError('Peer must be valid base32 ed25519 public key')
        
        socks = config.get('tor.socksport') # Load config for Tor socks port for proxy
        service_app = Flask(__name__) # Setup Flask app for server.
        service_port = get_open_port()
        service_ip = apiutils.setbindip.set_bind_IP()
        http_server = WSGIServer(('127.0.0.1', service_port), service_app, log=None)
        comm_inst.service_greenlets.append(http_server)

        # TODO define basic endpoints useful for direct connections like stats
        
        httpapi.load_plugin_blueprints(service_app, blueprint='direct_blueprint')

        @service_app.route('/ping')
        def get_ping():
            return "pong!"
        
        @service_app.route('/close')
        def shutdown_server():
            comm_inst.service_greenlets.remove(http_server)
            http_server.stop()
            return Response('goodbye')

        @service_app.after_request
        def afterReq(resp):
            # Security headers
            resp = httpheaders.set_default_onionr_http_headers(resp)
            return resp

        with Controller.from_port(port=config.get('tor.controlPort')) as controller:
            # Connect to the Tor process for Onionr
            controller.authenticate(config.get('tor.controlpassword'))
            # Create the v3 onion service for the peer to connect to
            response = controller.create_ephemeral_hidden_service({80: service_port}, await_publication = True, key_type='NEW', key_content = 'ED25519-V3')

            try:
                for x in range(3):
                    attempt = basicrequests.do_post_request(comm_inst.onionrInst, 'http://' + address + '/bs/' + response.service_id, port=socks)
                    if attempt == 'success':
                        break
                else:
                    raise ConnectionError
            except ConnectionError:
                # Re-raise
                raise ConnectionError('Could not reach %s bootstrap address %s' % (peer, address))
            else:
                # If no connection error, create the service and save it to local global key store
                self.onionr_inst.keyStore.put('dc-' + response.service_id, bytesconverter.bytes_to_str(peer))
                logger.info('hosting on %s with %s' % (response.service_id,  peer))
                http_server.serve_forever()
                http_server.stop()
                self.onionr_inst.keyStore.delete('dc-' + response.service_id)