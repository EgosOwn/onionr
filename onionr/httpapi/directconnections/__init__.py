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
from flask import Response, Blueprint

def _in_pool(pubkey, communicator):
    if pubkey in communicator.active_services


class DirectConnectionManagement:
    def __init__(self, client_api):
        direct_conn_management_bp = Blueprint('direct_conn_management', __name__)
        self.direct_conn_management_bp = direct_conn_management_bp
        communicator = client_api._too_many.get('OnionrCommunicatorDaemon')

        @direct_conn_management_bp.route('/isconnected/<pubkey>')
        def is_connected(pubkey):
            return