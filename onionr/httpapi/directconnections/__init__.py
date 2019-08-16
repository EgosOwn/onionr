'''
    Onionr - Private P2P Communication

    Misc client API endpoints too small to need their own file and that need access to the client api inst
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
import threading

from flask import Response
from flask import Blueprint
import deadsimplekv

import filepaths
import onionrservices

class DirectConnectionManagement:
    def __init__(self, client_api):
        direct_conn_management_bp = Blueprint('direct_conn_management', __name__)
        self.direct_conn_management_bp = direct_conn_management_bp
        communicator = client_api._too_many.get('OnionrCommunicatorDaemon')

        cache = communicator.deadsimplekv(filepaths.cached_storage)

        @direct_conn_management_bp.route('/dc-client/isconnected/<pubkey>')
        def is_connected(pubkey):
            resp = ""
            if pubkey in communicator.direct_connection_clients:
                resp = communicator.direct_connection_clients[pubkey]
            return Response(resp)
        
        @direct_conn_management_bp.route('/dc-client/connect/<pubkey>')
        def make_new_connection(pubkey):
            resp = "pending"
            if pubkey in communicator.direct_connection_clients:
                resp = communicator.active_services[pubkey]
            
            """Spawn a thread that will create the client and eventually add it to the
            communicator.active_services 
            """
            threading.Thread(target=onionrservices.OnionrServices().create_client, args=[pubkey, communicator]).start()

            return Response(resp)