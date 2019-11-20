'''
    Onionr - Private P2P Communication

    Shutdown the node either hard or cleanly
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
from flask import Blueprint, Response
from onionrblocks import onionrblockapi
import onionrexceptions
from onionrutils import stringvalidators
from coredb import daemonqueue
shutdown_bp = Blueprint('shutdown', __name__)

def shutdown(client_api_inst):
    try:
        client_api_inst.publicAPI.httpServer.stop()
        client_api_inst.httpServer.stop()
    except AttributeError:
        pass
    return Response("bye")

@shutdown_bp.route('/shutdownclean')
def shutdown_clean():
    # good for calling from other clients
    daemonqueue.daemon_queue_add('shutdown')
    return Response("bye")