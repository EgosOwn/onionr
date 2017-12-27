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
from flask import Flask, request
app = Flask(__name__)
import configparser, sys, random
'''
Main API
''' 
class API:
    
    def __init__(self, config, debug):
        self.config = config
        bindPort = int(self.config['CLIENT']['PORT'])
        clientToken = self.config['CLIENT']['CLIENT HMAC']

        if not debug:
            hostNums = [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]
            self.host = '127.' + str(hostNums[0]) + '.' + str(hostNums[1]) + '.' + str(hostNums[2])
        else:
            self.host = '127.0.0.1' 

        @app.route('/client/hello')
        def hello_world():
            self.validateHost()
            return 'Hello, World!' + request.host

        print('Starting client on ' + self.host + ':' + str(bindPort))
        print('Client token:', clientToken)

        app.run(host=self.host, port=bindPort, debug=True)
    
    def validateHost(self):
        # Validate host header, to protect against DNS rebinding attacks
        if request.host != '127.0.0.1:' + str(self.config['CLIENT']['PORT']):
            sys.exit(1)
        # Validate x-requested-with, to protect against CSRF/metadata leaks
        try:
            request.headers['x-requested-with']
        except:
            sys.exit(1)