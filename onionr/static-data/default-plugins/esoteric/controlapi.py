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
import core

core_inst = core.Core()
flask_blueprint = Blueprint('esoteric_control', __name__)

@flask_blueprint.route('/esoteric/ping')
def ping():
    return 'pong!'

@flask_blueprint.route('/esoteric/send/<peer>', methods=['POST'])
def send_message(peer):
    data = request.get_json(force=True)
    core_inst.keyStore.refresh()
    existing = core_inst.keyStore.get('s' + peer)
    if existing is None:
        existing = []
    existing.append(data)
    core_inst.keyStore.put('s' + peer, existing)
    core_inst.keyStore.flush()
    return Response('success')

@flask_blueprint.route('/esoteric/gets/<peer>')
def get_sent(peer):
    sent = core_inst.keyStore.get('s' + peer)
    if sent is None:
        sent = []
    return Response(json.dumps(sent))

@flask_blueprint.route('/esoteric/addrec/<peer>', methods=['POST'])
def add_rec(peer):
    data = request.get_json(force=True)
    core_inst.keyStore.refresh()
    existing = core_inst.keyStore.get('r' + peer)
    if existing is None:
        existing = []
    existing.append(data)
    core_inst.keyStore.put('r' + peer, existing)
    core_inst.keyStore.flush()
    return Response('success')

@flask_blueprint.route('/esoteric/getrec/<peer>')
def get_messages(peer):
    core_inst.keyStore.refresh()
    existing = core_inst.keyStore.get('r' + peer)
    if existing is None:
        existing = []
    else:
        existing = list(existing)
        core_inst.keyStore.delete('r' + peer)
    return Response(json.dumps(existing))