'''
    Onionr - Private P2P Communication

    This file handles all incoming http requests to the public api server, using Flask
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
import time
import flask
from gevent.pywsgi import WSGIServer
from httpapi import apiutils, security, fdsafehandler, miscpublicapi
import logger, onionr, filepaths
from utils import gettransports
class PublicAPI:
    '''
        The new client api server, isolated from the public api
    '''
    def __init__(self, clientAPI):
        config = clientAPI.config
        app = flask.Flask('PublicAPI')
        app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
        self.i2pEnabled = config.get('i2p.host', False)
        self.hideBlocks = [] # Blocks to be denied sharing
        self.host = apiutils.setbindip.set_bind_IP(filepaths.public_API_host_file)
        self.torAdder = gettransports.get()[0]
        self.bindPort = config.get('client.public.port')
        self.lastRequest = 0
        self.hitCount = 0 # total rec requests to public api since server started
        self.config = config
        self.clientAPI = clientAPI
        self.API_VERSION = onionr.API_VERSION
        logger.info('Running public api on %s:%s' % (self.host, self.bindPort))

        # Set instances, then startup our public api server
        clientAPI.setPublicAPIInstance(self)
        
        app.register_blueprint(security.public.PublicAPISecurity(self).public_api_security_bp)
        app.register_blueprint(miscpublicapi.endpoints.PublicEndpoints(self).public_endpoints_bp)
        self.httpServer = WSGIServer((self.host, self.bindPort), app, log=None, handler_class=fdsafehandler.FDSafeHandler)
        self.httpServer.serve_forever()