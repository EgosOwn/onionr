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
import socket, selectors, socks, config
import onionrexceptions, time, onionrchat
from dependencies import secrets
sel = selectors.DefaultSelector()

def getSocketCallbackRecieveHandler(coreInst, reason, create):
    '''Return the recieve handler function for a given socket reason'''
    retData = ''
    if startData == 'chat':
        retData = coreInst.chatInst.recieveMessage

def getSocketCallbackSendHandler(coreInst, reason, create):
    '''Return the send handler function for a given socket reason'''
    retData = ''
    if startData == 'chat':
        retData = coreInst.chatInst.sendMessage

class OnionrSockets:
    def __init__(self, coreInst, socketInfo):
        '''Create a new Socket object. This interface is named a bit misleadingly
        and does not actually forward network requests. 

        Accepts coreInst, an instance of Onionr core library, and socketInfo, a dict with these values:
        'peer': peer master public key
        'address': string, if we're connecting to a socket, this is the address we connect to. Not applicable if we're creating our own
        create: bool
        '''
        self.socketID = secrets.token_hex(32) # Generate an ID for this socket
        self._core = coreInst
        self.socketInfo = socketInfo
        
        # Make sure socketInfo provides all necessary values
        for i in ('peer', 'address', 'create', 'port'):
            try:
                socketInfo[i]
            except KeyError:
                raise ValueError('Must provide peer, address, and create in socketInfo dict argument')

        self.isServer = socketInfo['create'] # if we are the one creating the service

        self.remotePeer = socketInfo['peer']
        self.socketPort = socketInfo['port']
        self.serverAddress = socketInfo['address']
        self.connected = False

        self.readData = []
        self.sendData = 0

        if self.isServer:
            self.createServer()
        else:
            self.connectServer()
    
    def createServer(self):
        # Create our HS and advertise it via a block
        dataID = uuid.uuid4().hex
        ourAddress = ''
        ourPort = 1337
        ourInternalPort = 1338

        # Setup the empheral HS
        with stem.control.Controller.from_port() as controller:
            controller.authenticate()
            socketHS = controller.create_ephemeral_hidden_service({ourPort: ourInternalPort}, await_publication = True)
            ourAddress = socketHS.service_id

            # Advertise the server
            meta = {'address': ourAddress, 'port': ourPort}
            self._core.insertBlock(dataID, header='openSocket', encryptType='asym', asymPeer=self.remotePeer, sign=True, meta=meta)

            # Build the socket server
            sock = socket.socket()
            sock.bind(('127.0.0.1', ourInternalPort))
            sock.listen(100)
            sock.setblocking(False)
            sel.register(sock, selectors.EVENT_READ, self._accept)

            while True:
                events = sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)

        return

    def _accept(self, sock, mask):
        # Just accept the connection and pass it to our handler
        conn, addr = sock.accept()
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, self._read)
        self.connected = True

    def _read(self, conn, mask):
        data = conn.recv(1024)
        if data:
            data = data.decode()
            self.readData.append(data)
        else:
            sel.unregister(conn)
            conn.close()

    def sendData(self, data):
        try:
            data = data.encode()
        except AttributeError:
            pass
        self.sendData = data
    
    def readData(self):
        try:
            data = self.readData.pop(0)
        except IndexError:
            data = ''
        return data

    def connectServer(self):
        # Set the Tor proxy
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', config.get('tor.socksport'), rdns=True)
        socket.socket = socks.socksocket
        remoteSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with remoteSocket as s:
            s.connect((self.serverAddress, self.port))
            data = s.recv(1024)
            if self.sendData != 0:
                s.send(self.sendData)
                self.sendData = 0
        return