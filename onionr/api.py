'''
    Onionr - P2P Anonymous Storage Network

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
import flask
from flask import request, Response, abort, send_from_directory
from gevent.pywsgi import WSGIServer
import sys, random, threading, hmac, hashlib, base64, time, math, os, json
import core
from onionrblockapi import Block
import onionrutils, onionrexceptions, onionrcrypto, blockimporter, onionrevents as events, logger, config, onionr

def guessMime(path):
    '''
        Guesses the mime type from the input filename
    '''
    mimetypes = {
        'html' : 'text/html',
        'js' : 'application/javascript',
        'css' : 'text/css',
        'png' : 'image/png',
        'jpg' : 'image/jpeg'
    }

    for mimetype in mimetypes:
        if path.endswith('.%s' % mimetype):
            return mimetypes[mimetype]

    return 'text/plain'

def setBindIP(filePath):
    '''Set a random localhost IP to a specified file (intended for private or public API localhost IPs)'''
    hostOctets = [str(127), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF))]
    data = '.'.join(hostOctets)

    with open(filePath, 'w') as bindFile:
        bindFile.write(data)
    return data

class PublicAPI:
    '''
        The new client api server, isolated from the public api
    '''
    def __init__(self, clientAPI):
        assert isinstance(clientAPI, API)
        app = flask.Flask('PublicAPI')
        self.i2pEnabled = config.get('i2p.host', False)
        self.hideBlocks = [] # Blocks to be denied sharing
        self.host = setBindIP(clientAPI._core.publicApiHostFile)
        bindPort = config.get('client.public.port')

        @app.route('/')
        def banner():
            #validateHost('public')
            try:
                with open('static-data/index.html', 'r') as html:
                    resp = Response(html.read(), mimetype='text/html')
            except FileNotFoundError:
                resp = Response("")
            return resp
        clientAPI.setPublicAPIInstance(self)
        self.httpServer = WSGIServer((self.host, bindPort), app, log=None)
        self.httpServer.serve_forever()

class API:
    '''
        Client HTTP api
    '''

    callbacks = {'public' : {}, 'private' : {}}

    def __init__(self, debug, API_VERSION):
        '''
            Initialize the api server, preping variables for later use

            This initilization defines all of the API entry points and handlers for the endpoints and errors
            This also saves the used host (random localhost IP address) to the data folder in host.txt
        '''

        # configure logger and stuff
        onionr.Onionr.setupConfig('data/', self = self)

        self.debug = debug
        self._privateDelayTime = 3
        self._core = core.Core()
        self._crypto = onionrcrypto.OnionrCrypto(self._core)
        self._utils = onionrutils.OnionrUtils(self._core)
        app = flask.Flask(__name__)
        bindPort = int(config.get('client.client.port', 59496))
        self.bindPort = bindPort

        self.clientToken = config.get('client.webpassword')
        self.timeBypassToken = base64.b16encode(os.urandom(32)).decode()

        self.publicAPI = None # gets set when the thread calls our setter... bad hack but kinda necessary with flask
        threading.Thread(target=PublicAPI, args=(self,)).start()
        self.host = setBindIP(self._core.privateApiHostFile)
        logger.info('Running api on %s:%s' % (self.host, self.bindPort))
        self.httpServer = ''

        @app.route('/')
        def hello():
            return Response("hello client")
        
        @app.route('/shutdown')
        def shutdown():
            try:
                self.publicAPI.httpServer.stop()
                self.httpServer.stop()
            except AttributeError:
                pass
            return Response("bye")
        
        self.httpServer = WSGIServer((self.host, bindPort), app, log=None)
        self.httpServer.serve_forever()
    
    def setPublicAPIInstance(self, inst):
        assert isinstance(inst, PublicAPI)
        self.publicAPI = inst

    def validateToken(self, token):
        '''
            Validate that the client token matches the given token
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