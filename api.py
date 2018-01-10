'''
    Onionr - P2P Microblogging Platform & Social network
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
import configparser, sys, random, threading, hmac, hashlib, base64, time, math, gnupg

from core import Core
'''
Main API
''' 
class API:
    def validateToken(self, token):
        if self.clientToken != token:
            return False
        else:
            return True

    def __init__(self, config, debug):
        if os.path.exists('dev-enabled'):
            print('DEVELOPMENT MODE ENABLED (THIS IS LESS SECURE!)')
            self._developmentMode = True
        else:
            self._developmentMode = False
        self.config = config
        self.debug = debug
        self._privateDelayTime = 3
        self._core = Core()
        app = flask.Flask(__name__)
        bindPort = int(self.config['CLIENT']['PORT'])
        self.bindPort = bindPort
        self.clientToken = self.config['CLIENT']['CLIENT HMAC']

        if not debug:
            hostNums = [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]
            self.host = '127.' + str(hostNums[0]) + '.' + str(hostNums[1]) + '.' + str(hostNums[2])
        else:
            self.host = '127.0.0.1' 

        @app.before_request
        def beforeReq():
            self.requestFailed = False
            return

        @app.after_request
        def afterReq(resp):
            if not self.requestFailed:
                resp.headers['Access-Control-Allow-Origin'] = '*'
            else:
                resp.headers['server'] = 'Onionr'
            resp.headers['content-type'] = 'text/plain'
            resp.headers["Content-Security-Policy"] = "default-src 'none'"
            resp.headers['x-frame-options'] = 'deny'
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
            elif action == 'stats':
                resp = Response('something')
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
            if action == 'firstConnect':
                pass

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

        print('Starting client on ' + self.host + ':' + str(bindPort))
        print('Client token:', self.clientToken)

        app.run(host=self.host, port=bindPort, debug=True, threaded=True)
    
    def validateHost(self, hostType):
        if self.debug:
            return
        # Validate host header, to protect against DNS rebinding attacks
        host = self.host
        if hostType == 'private':
            if not request.host.startswith('127'):
                abort(403)
        elif hostType == 'public':
            if not request.host.endswith('onion') and not request.hosst.endswith('i2p'):
                abort(403)
        # Validate x-requested-with, to protect against CSRF/metadata leaks
        if self._developmentMode:
            try:
                request.headers['x-requested-with']
            except:
                # we exit rather than abort to avoid fingerprinting
                sys.exit(1)