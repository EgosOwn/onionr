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
from flask import request, Response
import configparser, sys, random
'''
Main API
''' 
class API:
    
    def __init__(self, config, debug):
        self.config = config
        self.debug = debug
        app = flask.Flask(__name__)
        bindPort = int(self.config['CLIENT']['PORT'])
        clientToken = self.config['CLIENT']['CLIENT HMAC']

        if not debug:
            hostNums = [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]
            self.host = '127.' + str(hostNums[0]) + '.' + str(hostNums[1]) + '.' + str(hostNums[2])
        else:
            self.host = '127.0.0.1' 

        @app.after_request
        def afterReq(resp):
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['server'] = 'Onionr'
            resp.headers['content-type'] = 'text/plain'
            resp.headers["Content-Security-Policy"] = "default-src 'none'"
            resp.headers['x-frame-options'] = 'deny'
            return resp
            
        @app.route('/client/hello')
        def hello_world():
            self.validateHost()
            resp = Response('Hello, World!' + request.host)
            return resp

        @app.errorhandler(404)
        def notfound(err):
            resp = Response("\_(0_0)_/ I got nothin")
            resp.headers = getHeaders(resp)
            return resp

        print('Starting client on ' + self.host + ':' + str(bindPort))
        print('Client token:', clientToken)

        app.run(host=self.host, port=bindPort, debug=True)
    
    def validateHost(self):
        if self.debug:
            return
        # Validate host header, to protect against DNS rebinding attacks
        if request.host != '127.0.0.1:' + str(self.config['CLIENT']['PORT']):
            sys.exit(1)
        # Validate x-requested-with, to protect against CSRF/metadata leaks
        try:
            request.headers['x-requested-with']
        except:
            sys.exit(1)
