'''
    Onionr - Private P2P Communication

    Onionr services provide the server component to direct connections
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
import time
import stem
import core
from . import connectionserver, bootstrapservice

class OnionrServices:
    '''
        Create a client or server for connecting to peer interfaces
    '''
    def __init__(self, onionr_core):
        assert isinstance(onionr_core, core.Core)
        self._core = onionr_core
        self.servers = {}
        self.clients = {}
        self.shutdown = False
        return
    
    def create_server(self, peer, address):
        '''
            When a client wants to connect, contact their bootstrap address and tell them our
            ephemeral address for our service by creating a new ConnectionServer instance
        '''
        assert self._core._utils.validateID(address)
        BOOTSTRAP_TRIES = 10 # How many times to attempt contacting the bootstrap server
        TRY_WAIT = 3 # Seconds to wait before trying bootstrap again
        # HTTP is fine because .onion/i2p is encrypted/authenticated
        base_url = 'http://%s/' % (address,)
        socks = self._core.config.get('tor.socksport')
        for x in range(BOOTSTRAP_TRIES):
            if self._core._utils.doGetRequest(base_url + 'ping', port=socks, ignoreAPI=True) == 'pong!':
                # if bootstrap sever is online, tell them our service address
                connectionserver.ConnectionServer(peer, address, core_inst=self._core)
            else:
                time.sleep(TRY_WAIT)
        else:
            return False

    def create_client(self, peer):
        # Create ephemeral onion service to bootstrap connection
        address = bootstrapservice.bootstrap_client_service(peer)
        return address