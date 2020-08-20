"""Onionr - Private P2P Communication.

Onionr services provide the server component to direct connections
"""
import time
from . import connectionserver, bootstrapservice, serverexists
from onionrutils import stringvalidators, basicrequests
import config
"""
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
"""

server_exists = serverexists.server_exists


class OnionrServices:
    """Create a client or server for connecting to peer interfaces."""
    def __init__(self):
        self.servers = {}
        self.clients = {}
        self.shutdown = False

    def create_server(self, peer, address, comm_inst):
        """
        Create a server for direct connections

        When a client wants to connect, contact their bootstrap address and tell them our ephemeral address for our service by creating a new ConnectionServer instance
        """
        if not stringvalidators.validate_transport(address):
            raise ValueError('address must be valid')
        # How many times to attempt contacting the bootstrap server
        BOOTSTRAP_TRIES = 10
        # Seconds to wait before trying bootstrap again
        TRY_WAIT = 3
        # HTTP is fine because .onion/i2p is encrypted/authenticated
        base_url = 'http://%s/' % (address,)
        socks = config.get('tor.socksport')
        for x in range(BOOTSTRAP_TRIES):
            if basicrequests.do_get_request(
                    base_url + 'ping', port=socks, ignoreAPI=True) == 'pong!':
                # if bootstrap sever is online, tell them our service address
                connectionserver.ConnectionServer(
                    peer, address, comm_inst=comm_inst)
            else:
                time.sleep(TRY_WAIT)
        else:
            return False

    @staticmethod
    def create_client(peer, comm_inst=None):
        # Create ephemeral onion service to bootstrap connection to server
        if comm_inst is not None:
            try:
                return comm_inst.direct_connection_clients[peer]
            except KeyError:
                pass
        address = bootstrapservice.bootstrap_client_service(peer, comm_inst)
        return address
