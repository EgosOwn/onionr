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
import threading
import socks, config, uuid
import onionrexceptions, time, requests, onionrblockapi, logger
from dependencies import secrets
from gevent.pywsgi import WSGIServer
from flask import request, Response, abort
import flask
class OnionrSocketServer:
    def __init__(self, coreInst):
        self._core = coreInst
        app = flask.Flask(__name__)
        self._core.socketServerConnData = {}
        self.bindPort = 0

        self.sockets = {}

        while self.bindPort < 1024:
            self.bindPort = secrets.randbelow(65535)

        self.responseData = {}

        threading.Thread(target=self.detectShutdown).start()
        threading.Thread(target=self.socketStarter).start()
        app = flask.Flask(__name__)
        self.http_server = WSGIServer(('127.0.0.1', self.bindPort), app)
        self.http_server.serve_forever()

        @app.route('/dc/', methods=['POST'])
        def acceptConn(self):
            data = request.form['data']
            data = self._core._utils.bytesTorStr(data)
            data = {'date': self._core._utils.getEpoch(), 'data': data}
            myPeer = ''
            retData = ''
            for peer in self.sockets:
                if self.sockets[peer] == request.host:
                    myPeer = peer
                    break
            else:
                return ""

            if request.host in self.sockets:
                self._core.socketServerConnData[myPeer].append(data)
            else:
                self._core.socketServerConnData[myPeer] = [data]

            try:
                retData = self._core.socketServerResponseData[myPeer]
            except KeyError:
                pass

            self._core.socketServerConnData[myPeer] = ''

            return retData
    
    def socketStarter(self):
        while not self._core.killSockets:
            try:
                self.addSocket(self._core.startSocket['peer'], reason=self._core.startSocket['reason'])
            except KeyError:
                pass
            else:
                logger.info('%s socket started with %s' % (self._core.startSocket['reason'], self._core.startSocket['peer']))
                self._core.startSocket = {}
            time.sleep(1)

    def detectShutdown(self):
        while not self._core.killSockets:
            time.sleep(5)
        logger.info('Killing socket server')
        self.http_server.stop()

    def addSocket(self, peer, reason=''):
        bindPort = 1337

        assert len(reason) <= 12
            
        with stem.control.Controller.from_port(port=config.get('tor.controlPort')) as controller:
            controller.authenticate(config.get('tor.controlpassword'))

            socket = controller.create_ephemeral_hidden_service({80: bindPort}, await_publication = True)
            self.sockets[peer] = socket.service_id

            self.responseData[socket.service_id] = ''

            self._core.insertBlock(str(uuid.uuid4()), header='socket', sign=True, encryptType='asym', asymPeer=peer, meta={'reason': reason})
            self._core.socketReasons[peer] = reason
        return
    
class OnionrSocketClient:
    def __init__(self, coreInst):
        self.sockets = {} # pubkey: tor address
        self.connPool = {}
        self.sendData = {}
        self._core = coreInst
        self.response = ''
        self.request = ''
        self.connected = False
        self.killSocket = False

    def startSocket(self, peer, reason):
        address = ''
        logger.info('Trying to find socket server for %s' % (peer,))
        # Find the newest open socket for a given peer
        for block in self._core.getBlocksByType('socket'):
            block = onionrblockapi.Block(block, core=self._myCore)
            if block.decrypt():
                if block.verifySig() and block.signer == peer:
                    address = block.getMetadata('address')
                    if self._core._utils.validateID(address):
                        # If we got their address, it is valid, and verified, we can break out
                        if block.getMetadata('reason') == 'chat':
                            break
                    else:
                        address = ''
        if address != '':
            logger.info('%s socket client started with %s' % (reason, peer))
            self.sockets[peer] = address
            data = 'hey'
            while not self.killSocket:
                try:
                    data = self.sendData[peer]
                except KeyError:
                    pass
                else:
                    self.sendData[peer] = ''
                postData = {'data': data}
                self.connPool[peer] = {'date': self._core._utils.getEpoch(), 'data': self._core._utils.doPostRequest('http://' + address + '/dc/', data=postData)}
    
    def getResponse(self, peer):
        retData = ''
        try:
            retData = self.connPool[peer]
        except KeyError:
            pass
        return
    
    def sendData(self, peer, data):
        self.sendData[peer] = data