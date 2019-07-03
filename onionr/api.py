'''
    Onionr - Private P2P Communication

    This file handles all incoming http requests to the client, using Flask
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
import threading, hmac, base64, time, os
from gevent.pywsgi import WSGIServer
import flask
from flask import request, Response, abort, send_from_directory
import core
import onionrexceptions, onionrcrypto, logger, config
import httpapi
from httpapi import friendsapi, profilesapi, configapi, miscpublicapi, miscclientapi, insertblock, onionrsitesapi
from onionrservices import httpheaders
import onionr
from onionrutils import bytesconverter, stringvalidators, epoch, mnemonickeys
from httpapi import apiutils, security, fdsafehandler

config.reload()

class PublicAPI:
    '''
        The new client api server, isolated from the public api
    '''
    def __init__(self, clientAPI):
        assert isinstance(clientAPI, API)
        app = flask.Flask('PublicAPI')
        app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
        self.i2pEnabled = config.get('i2p.host', False)
        self.hideBlocks = [] # Blocks to be denied sharing
        self.host = apiutils.setbindip.set_bind_IP(clientAPI._core.publicApiHostFile, clientAPI._core)
        self.torAdder = clientAPI._core.hsAddress
        self.i2pAdder = clientAPI._core.i2pAddress
        self.bindPort = config.get('client.public.port')
        self.lastRequest = 0
        self.hitCount = 0 # total rec requests to public api since server started
        self.config = config
        self.clientAPI = clientAPI
        self.API_VERSION = onionr.API_VERSION
        logger.info('Running public api on %s:%s' % (self.host, self.bindPort))

        # Set instances, then startup our public api server
        clientAPI.setPublicAPIInstance(self)
        while self.torAdder == '':
            clientAPI._core.refreshFirstStartVars()
            self.torAdder = clientAPI._core.hsAddress
            time.sleep(0.1)
        
        app.register_blueprint(security.public.PublicAPISecurity(self).public_api_security_bp)
        app.register_blueprint(miscpublicapi.endpoints.PublicEndpoints(self).public_endpoints_bp)
        self.httpServer = WSGIServer((self.host, self.bindPort), app, log=None, handler_class=fdsafehandler.FDSafeHandler)
        self.httpServer.serve_forever()

class API:
    '''
        Client HTTP api
    '''

    callbacks = {'public' : {}, 'private' : {}}

    def __init__(self, onionrInst, debug, API_VERSION):
        '''
            Initialize the api server, preping variables for later use

            This initialization defines all of the API entry points and handlers for the endpoints and errors
            This also saves the used host (random localhost IP address) to the data folder in host.txt
        '''

        self.debug = debug
        self._core = onionrInst.onionrCore
        self.startTime = epoch.get_epoch()
        self._crypto = onionrcrypto.OnionrCrypto(self._core)
        app = flask.Flask(__name__)
        bindPort = int(config.get('client.client.port', 59496))
        self.bindPort = bindPort

        self.clientToken = config.get('client.webpassword')
        self.timeBypassToken = base64.b16encode(os.urandom(32)).decode()

        self.publicAPI = None # gets set when the thread calls our setter... bad hack but kinda necessary with flask
        #threading.Thread(target=PublicAPI, args=(self,)).start()
        self.host = apiutils.setbindip.set_bind_IP(self._core.privateApiHostFile, self._core)
        logger.info('Running api on %s:%s' % (self.host, self.bindPort))
        self.httpServer = ''

        self.queueResponse = {}
        onionrInst.setClientAPIInst(self)
        app.register_blueprint(security.client.ClientAPISecurity(self).client_api_security_bp)
        app.register_blueprint(friendsapi.friends)
        app.register_blueprint(profilesapi.profile_BP)
        app.register_blueprint(configapi.config_BP)
        app.register_blueprint(insertblock.ib)
        app.register_blueprint(miscclientapi.getblocks.client_get_blocks)
        app.register_blueprint(miscclientapi.staticfiles.static_files_bp)
        app.register_blueprint(miscclientapi.endpoints.PrivateEndpoints(self).private_endpoints_bp)
        app.register_blueprint(onionrsitesapi.site_api)
        app.register_blueprint(apiutils.shutdown.shutdown_bp)
        httpapi.load_plugin_blueprints(app)
        self.get_block_data = apiutils.GetBlockData(self)

        self.httpServer = WSGIServer((self.host, bindPort), app, log=None, handler_class=fdsafehandler.FDSafeHandler)
        self.httpServer.serve_forever()

    def setPublicAPIInstance(self, inst):
        assert isinstance(inst, PublicAPI)
        self.publicAPI = inst

    def validateToken(self, token):
        '''
            Validate that the client token matches the given token. Used to prevent CSRF and data exfiltration
        '''
        if len(self.clientToken) == 0:
            logger.error("client password needs to be set")
            return False
        try:
            if not hmac.compare_digest(self.clientToken, token):
                return False
            else:
                return True
        except TypeError:
            return False

    def getUptime(self):
        while True:
            try:
                return epoch.get_epoch() - self.startTime
            except (AttributeError, NameError):
                # Don't error on race condition with startup
                pass

    def getBlockData(self, bHash, decrypt=False, raw=False, headerOnly=False):
        return self.get_block_data.get_block_data(bHash, decrypt=decrypt, raw=raw, headerOnly=headerOnly)
