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
import base64, os, time
import flask
from gevent.pywsgi import WSGIServer
from onionrutils import epoch
import httpapi, filepaths, logger
from . import register_private_blueprints
from etc import waitforsetvar
import serializeddata, config
from .. import public
class PrivateAPI:
    '''
        Client HTTP api
    '''

    callbacks = {'public' : {}, 'private' : {}}

    def __init__(self):
        '''
            Initialize the api server, preping variables for later use

            This initialization defines all of the API entry points and handlers for the endpoints and errors
            This also saves the used host (random localhost IP address) to the data folder in host.txt
        '''
        self.config = config
        self.startTime = epoch.get_epoch()
        app = flask.Flask(__name__)
        bindPort = int(config.get('client.client.port', 59496))
        self.bindPort = bindPort

        self.clientToken = config.get('client.webpassword')
        self.timeBypassToken = base64.b16encode(os.urandom(32)).decode()

        self.host = httpapi.apiutils.setbindip.set_bind_IP(filepaths.private_API_host_file)
        logger.info('Running api on %s:%s' % (self.host, self.bindPort))
        self.httpServer = ''

        self.queueResponse = {}
        self.get_block_data = httpapi.apiutils.GetBlockData(self)
        register_private_blueprints.register_private_blueprints(self, app)
        httpapi.load_plugin_blueprints(app)
        self.app = app
    
    def start(self):
        waitforsetvar.wait_for_set_var(self, "_too_many")
        self.publicAPI = self._too_many.get(public.PublicAPI)
        self.httpServer = WSGIServer((self.host, self.bindPort), self.app, log=None, handler_class=httpapi.fdsafehandler.FDSafeHandler)
        self.httpServer.serve_forever()

    def setPublicAPIInstance(self, inst):
        self.publicAPI = inst

    def validateToken(self, token):
        '''
            Validate that the client token matches the given token. Used to prevent CSRF and data exfiltration
        '''
        if not self.clientToken:
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
