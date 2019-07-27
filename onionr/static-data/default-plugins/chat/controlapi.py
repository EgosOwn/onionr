'''
    Onionr - Private P2P Communication

    HTTP endpoints for controlling IMs
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
import json
from flask import Response, request, redirect, Blueprint, send_from_directory
import deadsimplekv as simplekv
import filepaths
flask_blueprint = Blueprint('chat_control', __name__)
key_store = simplekv.DeadSimpleKV(filepaths.cached_storage, refresh_seconds=5)
@flask_blueprint.route('/chatapi/ping')
def ping():
    return 'pong!'

@flask_blueprint.route('/chatapi/send/<peer>', methods=['POST'])
def send_message(peer):
    data = request.get_json(force=True)
    key_store.refresh()
    existing = key_store.get('s' + peer)
    if existing is None:
        existing = []
    existing.append(data)
    key_store.put('s' + peer, existing)
    key_store.flush()
    return Response('success')

@flask_blueprint.route('/chatapi/gets/<peer>')
def get_sent(peer):
    sent = key_store.get('s' + peer)
    if sent is None:
        sent = []
    return Response(json.dumps(sent))

@flask_blueprint.route('/chatapi/addrec/<peer>', methods=['POST'])
def add_rec(peer):
    data = request.get_json(force=True)
    key_store.refresh()
    existing = key_store.get('r' + peer)
    if existing is None:
        existing = []
    existing.append(data)
    key_store.put('r' + peer, existing)
    key_store.flush()
    return Response('success')

@flask_blueprint.route('/chatapi/getrec/<peer>')
def get_messages(peer):
    key_store.refresh()
    existing = key_store.get('r' + peer)
    if existing is None:
        existing = []
    else:
        existing = list(existing)
        key_store.delete('r' + peer)
    return Response(json.dumps(existing))