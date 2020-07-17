"""Onionr - Private P2P Communication.

HTTP endpoints for communicating with peers
"""
import sys
import os
from json import JSONDecodeError

import deadsimplekv as simplekv
import ujson as json
from flask import Response, request, redirect, Blueprint, abort, g

from utils import identifyhome
from onionrutils import localcommand
import filepaths
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
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
direct_blueprint = Blueprint('chat', __name__)

key_store = simplekv.DeadSimpleKV(filepaths.cached_storage, refresh_seconds=5)
storage_dir = identifyhome.identify_home()

@direct_blueprint.before_request
def request_setup():
    key_store.refresh()
    host = request.host
    host = host.strip('.b32.i2p')
    host = host.strip('.onion')
    g.host = host
    g.peer = key_store.get('dc-' + g.host)

@direct_blueprint.route('/chat/ping')
def pingdirect():
    return 'pong!'

@direct_blueprint.route('/chat/sendto', methods=['POST', 'GET'])
def sendto():
    """Endpoint peers send chat messages to"""
    try:
        msg = request.get_json(force=True)
    except JSONDecodeError:
        msg = ''
    else:
        msg = json.dumps(msg)
        localcommand.local_command('/chat/addrec/%s' % (g.peer,), post=True, post_data=msg)
    return Response('success')

@direct_blueprint.route('/chat/poll')
def poll_chat():
    """Endpoints peers get new messages from"""
    return Response(localcommand.local_command('/chat/gets/%s' % (g.peer,)))
    