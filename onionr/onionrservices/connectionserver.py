'''
    Onionr - P2P Anonymous Storage Network

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
import threading, time
from gevent.pywsgi import WSGIServer, WSGIHandler
from stem.control import Controller
from flask import Flask
import core, logger, httpapi
from netcontroller import getOpenPort
import api
from . import httpheaders

class ConnectionServer:
    def __init__(self, peer, address, core_inst=None):
        if core_inst is None:
            self.core_inst = core.Core()
        else:
            self.core_inst = core_inst

        if not core_inst._utils.validatePubKey(peer):
            raise ValueError('Peer must be valid base32 ed25519 public key')
        
        socks = core_inst.config.get('tor.socksport') # Load config for Tor socks port for proxy
        service_app = Flask(__name__) # Setup Flask app for server.
        service_port = getOpenPort()
        service_ip = api.setBindIP()
        http_server = WSGIServer(('127.0.0.1', service_port), service_app, log=None)
        core_inst.onionrInst.communicatorInst.service_greenlets.append(http_server)

        # TODO define basic endpoints useful for direct connections like stats
        
        httpapi.load_plugin_blueprints(service_app, blueprint='direct_blueprint')

        @service_app.route('/ping')
        def get_ping():
            return "pong!"
        
        @service_app.route('/shutdown')
        def shutdown_server():
            core_inst.onionrInst.communicatorInst.service_greenlets.remove(http_server)
            http_server.stop()
            return Response('goodbye')

        @service_app.after_request
        def afterReq(resp):
            # Security headers
            resp = httpheaders.set_default_onionr_http_headers(resp)
            return resp

        with Controller.from_port(port=core_inst.config.get('tor.controlPort')) as controller:
            # Connect to the Tor process for Onionr
            controller.authenticate(core_inst.config.get('tor.controlpassword'))
            # Create the v3 onion service
            response = controller.create_ephemeral_hidden_service({80: service_port}, await_publication = True, key_type='NEW', key_content = 'ED25519-V3')
            self.core_inst.keyStore.put('dc-' + response.service_id, self.core_inst._utils.bytesToStr(peer))
            self.core_inst._utils.doPostRequest('http://' + address + '/bs/' + response.service_id, port=socks)
            logger.info('hosting on %s with %s' % (response.service_id,  peer))
            http_server.serve_forever()
            self.core_inst.keyStore.delete('dc-' + response.service_id)
            http_server.stop()