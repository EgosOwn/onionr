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
import socket, selectors
import onionrexceptions
from dependencies import secrets

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

        if self.isServer:
            self.createServer()
    
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

        meta = {'address': ourAddress, 'port': ourPort}
        self._core.insertBlock(dataID, header='openSocket', encryptType='asym', asymPeer=self.remotePeer, sign=True, meta=meta)
        return