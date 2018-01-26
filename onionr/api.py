'''
    Onionr - P2P Microblogging Platform & Social network

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
from flask import request, Response, abort
from multiprocessing import Process
import configparser, sys, random, threading, hmac, hashlib, base64, time, math, gnupg, os, logging

from core import Core
import onionrutils
class API:
    ''' Main http api (flask)'''
    def validateToken(self, token):
        '''
        Validate if the client token (hmac) matches the given token
        '''
        if self.clientToken != token:
            return False
        else:
            return True

    def __init__(self, config, debug):
        ''' Initialize the api server, preping variables for later use
        This initilization defines all of the API entry points and handlers for the endpoints and errors

        This also saves the used host (random localhost IP address) to the data folder in host.txt
        '''
        if os.path.exists('dev-enabled'):
            self._developmentMode = True
            logger.set_level(logger.LEVEL_DEBUG)
            logger.warn('DEVELOPMENT MODE ENABLED (THIS IS LESS SECURE!)')
        else:
            self._developmentMode = False
            logger.set_level(logger.LEVEL_INFO)

        self.config = config
        self.debug = debug
        self._privateDelayTime = 3
        self._core = Core()
        self._utils = onionrutils.OnionrUtils(self._core)
        app = flask.Flask(__name__)
        bindPort = int(self.config['CLIENT']['PORT'])
        self.bindPort = bindPort
        self.clientToken = self.config['CLIENT']['CLIENT HMAC']
        logger.debug('Your HMAC token: ' + logger.colors.underline + self.clientToken)

        if not debug and not self._developmentMode:
            hostNums = [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]
            self.host = '127.' + str(hostNums[0]) + '.' + str(hostNums[1]) + '.' + str(hostNums[2])
        else:
            self.host = '127.0.0.1'
        hostFile = open('data/host.txt', 'w')
        hostFile.write(self.host)
        hostFile.close()

        @app.before_request
        def beforeReq():
            '''
            Simply define the request as not having yet failed, before every request.
            '''
            self.requestFailed = False
            return

        @app.after_request
        def afterReq(resp):
            if not self.requestFailed:
                resp.headers['Access-Control-Allow-Origin'] = '*'
            else:
                resp.headers['server'] = 'Onionr'
            resp.headers['Content-Type'] = 'text/plain'
            resp.headers["Content-Security-Policy"] = "default-src 'none'"
            resp.headers['X-Frame-Options'] = 'deny'
            return resp

        @app.route('/client/')
        def private_handler():
            startTime = math.floor(time.time())
            # we should keep a hash DB of requests (with hmac) to prevent replays
            action = request.args.get('action')
            #if not self.debug:
            token = request.args.get('token')
            if not self.validateToken(token):
                abort(403)
            self.validateHost('private')
            if action == 'hello':
                resp = Response('Hello, World! ' + request.host)
            elif action == 'shutdown':
                request.environ.get('werkzeug.server.shutdown')()
                resp = Response('Goodbye')
            elif action == 'stats':
                resp = Response('me_irl')
            elif action == 'init':
                # generate PGP key
                self._core.generateMainPGP()
                pass
            else:
                resp = Response('(O_o) Dude what? (invalid command)')
            endTime = math.floor(time.time())
            elapsed = endTime - startTime
            if elapsed < self._privateDelayTime:
                time.sleep(self._privateDelayTime - elapsed)
            return resp

        @app.route('/public/')
        def public_handler():
            # Public means it is publicly network accessible
            self.validateHost('public')
            action = request.args.get('action')
            requestingPeer = request.args.get('myID')
            data = request.args.get('data')
            if action == 'firstConnect':
                pass
            elif action == 'ping':
                resp = Response("pong!")
            elif action == 'setHMAC':
                pass
            elif action == 'getDBHash':
                resp = Response(self._utils.getBlockDBHash())
            elif action == 'getBlockHashes':
                resp = Response(self._core.getBlockList())
            elif action == 'getPGP':
                resp = Response(self._utils.exportMyPubkey())
            # setData should be something the communicator initiates, not this api
            elif action == 'getData':
                resp = Response(self._core.getData(data))

            return resp

        @app.errorhandler(404)
        def notfound(err):
            self.requestFailed = True
            resp = Response("")
            #resp.headers = getHeaders(resp)
            return resp
        @app.errorhandler(403)
        def authFail(err):
            self.requestFailed = True
            resp = Response("403")
            return resp
        @app.errorhandler(401)
        def clientError(err):
            self.requestFailed = True
            resp = Response("Invalid request")
            return resp

        logger.info('Starting client on ' + self.host + ':' + str(bindPort) + '...')
        logger.debug('Client token: ' + logger.colors.underline + self.clientToken)

        app.run(host=self.host, port=bindPort, debug=True, threaded=True)

    def validateHost(self, hostType):
        ''' Validate various features of the request including:
            If private (/client/), is the host header local?
            If public (/public/), is the host header onion or i2p?

            Was X-Request-With used?
        '''
        if self.debug:
            return
        # Validate host header, to protect against DNS rebinding attacks
        host = self.host
        if hostType == 'private':
            if not request.host.startswith('127'):
                abort(403)
        elif hostType == 'public':
            if not request.host.endswith('onion') and not request.host.endswith('i2p'):
                abort(403)
        # Validate x-requested-with, to protect against CSRF/metadata leaks
        if not self._developmentMode:
            try:
                request.headers['X-Requested-With']
            except:
                # we exit rather than abort to avoid fingerprinting
                logger.debug('Avoiding fingerprinting, exiting...')
                sys.exit(1)
