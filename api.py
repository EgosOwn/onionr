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
import configparser, sys, random, threading, hmac, hashlib, base64

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
        self.config = config
        self.debug = debug
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
            return

        @app.after_request
        def afterReq(resp):
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['server'] = 'Onionr'
            resp.headers['content-type'] = 'text/plain'
            resp.headers["Content-Security-Policy"] = "default-src 'none'"
            resp.headers['x-frame-options'] = 'deny'
            return resp
            
        @app.route('/client/')
        def private_handler():
            # we should keep a hash DB of requests (with hmac) to prevent replays
            action = request.args.get('action')
            #if not self.debug:
            token = request.args.get('token')
            if not self.validateToken(token):
                abort(403)
            self.validateHost()
            if action == 'hello':
                resp = Response('Hello, World! ' + request.host)
            elif action == 'stats':
                resp =Response('something')
            else:
                resp = Response('(O_o) Dude what? (invalid command)')
            return resp

        @app.errorhandler(404)
        def notfound(err):
            resp = Response("\_(0_0)_/ I got nothin")
            #resp.headers = getHeaders(resp)
            return resp
        @app.errorhandler(403)
        def authFail(err):
            resp = Response("Auth required/security failure")
            return resp

        print('Starting client on ' + self.host + ':' + str(bindPort))
        print('Client token:', self.clientToken)

        app.run(host=self.host, port=bindPort, debug=True, threaded=True)
    
    def validateHost(self):
        if self.debug:
            return
        # Validate host header, to protect against DNS rebinding attacks
        host = self.host
        if not request.host.startswith('127'):
            abort(403)
        # Validate x-requested-with, to protect against CSRF/metadata leaks
        '''
        try:
            request.headers['x-requested-with']
        except:
            # we exit rather than abort to avoid fingerprinting
            sys.exit(1)
        '''