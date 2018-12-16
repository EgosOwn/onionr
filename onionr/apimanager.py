'''
    Onionr - P2P Anonymous Storage Network

    Handles api data exchange, interfaced by both public and client http api
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
import config, apipublic, apiprivate, core, socket, random, threading, time
config.reload()

PRIVATE_API_VERSION = 0
PUBLIC_API_VERSION = 1

DEV_MODE = config.get('general.dev_mode')

def getOpenPort():
    '''Get a random open port'''
    p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p.bind(("127.0.0.1",0))
    p.listen(1)
    port = s.getsockname()[1]
    p.close()
    return port

def getRandomLocalIP():
    '''Get a random local ip address'''
    hostOctets = [str(127), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF)), str(random.randint(0x02, 0xFF))]
    host = '.'.join(hostOctets)
    return host

class APIManager:
    def __init__(self, coreInst):
        assert isinstance(coreInst, core.Core)
        self.core = core
        self.utils = core._utils
        self.crypto = core._crypto
        
        # if this gets set to true, both the public and private apis will shutdown
        self.shutdown = False
        
        publicIP = '127.0.0.1'
        privateIP = '127.0.0.1'
        if DEV_MODE:
            # set private and local api servers bind IPs to random localhost (127.x.x.x), make sure not the same
            privateIP = getRandomLocalIP()
            while True:
                publicIP = getRandomLocalIP()
                if publicIP != privateIP:
                    break
        
        # Make official the IPs and Ports
        self.publicIP = publicIP
        self.privateIP = privateIP
        self.publicPort = getOpenPort()
        self.privatePort = getOpenPort()

        # Run the API servers in new threads
        self.publicAPI = apipublic.APIPublic()
        self.privateAPI = apiprivate.privateAPI()
        threading.Thread(target=self.publicAPI.run).start()
        threading.Thread(target=self.privateAPI.run).start()
        while not self.shutdown:
            time.sleep(1)