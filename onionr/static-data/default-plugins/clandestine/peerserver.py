'''
    Onionr - P2P Anonymous Storage Network

    HTTP endpoints for communicating with peers
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
import core
from flask import Response, request, redirect, Blueprint, abort, g

direct_blueprint = Blueprint('clandestine', __name__)
core_inst = core.Core()

storage_dir = core_inst.dataDir

@direct_blueprint.before_request
def request_setup():
    core_inst.keyStore.refresh()
    host = request.host
    host = host.strip('.b32.i2p')
    host = host.strip('.onion')
    g.host = host
    g.peer = core_inst.keyStore.get('dc-' + g.host)

@direct_blueprint.route('/clandestine/ping')
def pingdirect():
    return 'pong!' + g.peer

@direct_blueprint.route('/clandestine/send')
def poll_chat