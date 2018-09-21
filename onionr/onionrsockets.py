'''
    Onionr - P2P Anonymous Storage Network

    Onionr Socket interface
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
import stem.control
import socks, config, uuid
import onionrexceptions, time, requests
from dependencies import secrets
from flask import request, Response, abort

class OnionrSocketServer:
    def __init__(self, coreInst):
        self.sockets = {} # pubkey: tor address
        self.connPool = {}
        self.bindPort = 1337
        self._core = coreInst
        self.responseData = {}
        self.killSocket = False
        app = flask.Flask(__name__)
        
        http_server = WSGIServer((socket.service_id, bindPort), app)
        http_server.serve_forever()

    @app.route('/dc/', methods=['POST'])
    def acceptConn(self):
        data = request.form['data']
        data = self._core._utils.bytesTorStr(data)

        if request.host in self.connPool:
            self.connPool[request.host].append(data)
        else:
            self.connPool[request.host] = [data]

        retData = self.responseData[request.host]

        self.responseData[request.host] = ''

        return retData
    
    def setResponseData(self, host, data):
        self.responseData[host] = data

    def addSocket(self, peer):
        bindPort = 1337
        with stem.control.Controller.from_port(port=config.get('tor.controlPort')) as controller:
            controller.authenticate(config.get('tor.controlpassword'))

            socket = controller.create_ephemeral_hidden_service({80: bindPort}, await_publication = True)
            self.sockets[peer] = socket.service_id

            self.responseData[socket.service_id] = ''

            self._core.insertBlock(uuid.uuid4(), header='startSocket', sign=True, encryptType='asym', asymPeer=peer, meta={})

            while not self.killSocket:
                time.sleep(3)
        return
    
class OnionrSocketClient:
    def __init__(self, coreInst):
        self.sockets = {} # pubkey: tor address
        self.connPool = {}
        self.bindPort = 1337
        self._core = coreInst
        self.response = ''
        self.request = ''
        self.connected = False

    def getResponse(self, peer):
        self._core._utils.doPostRequest(self.)