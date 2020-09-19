"""Onionr - Private P2P Communication.

HTTP endpoints for mail plugin
"""
import sys
import os

import ujson as json
from flask import Response, request, redirect, Blueprint, abort
from flask import send_from_directory
import deadsimplekv as simplekv

from httpapi.sse.wrapper import SSEWrapper
from onionrusers import contactmanager
from onionrutils import stringvalidators
from utils import reconstructhash, identifyhome
from utils.bettersleep import better_sleep as sleep

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import loadinbox
import sentboxdb
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
flask_blueprint = Blueprint('mail', __name__)
kv = simplekv.DeadSimpleKV(identifyhome.identify_home() + '/mailcache.dat')
root = os.path.dirname(os.path.realpath(__file__))

sse_wrapper = SSEWrapper()

@flask_blueprint.route('/mail/<path:path>', endpoint='mailstatic')
def load_mail(path):
    return send_from_directory(root + '/web/', path)


@flask_blueprint.route('/mail/', endpoint='mailindex')
def load_mail_index():
    return send_from_directory(root + '/web/', 'index.html')


@flask_blueprint.route('/mail/ping')
def mail_ping():
    return 'pong!'

@flask_blueprint.route('/mail/deletemsg/<block>', methods=['POST'])
def mail_delete(block):
    if not stringvalidators.validate_hash(block):
        abort(504)
    block = reconstructhash.deconstruct_hash(block)
    existing = kv.get('deleted_mail')
    if existing is None:
        existing = []
    if block not in existing:
        existing.append(block)
    kv.put('deleted_mail', existing)
    kv.flush()
    return 'success'

@flask_blueprint.route('/mail/getinbox')
def list_inbox():
    return ','.join(loadinbox.load_inbox())


@flask_blueprint.route('/mail/streaminbox')
def stream_inbox():
    def _stream():
        while True:
            yield "data: " + ','.join(loadinbox.load_inbox()) + "\n\n"
            sleep(1)
    return sse_wrapper.handle_sse_request(_stream)


@flask_blueprint.route('/mail/getsentbox')
def list_sentbox():
    kv.refresh()
    sentbox_list = sentboxdb.SentBox().listSent()
    list_copy = list(sentbox_list)
    deleted = kv.get('deleted_mail')
    if deleted is None:
        deleted = []
    for sent in list_copy:
        if sent['hash'] in deleted:
            sentbox_list.remove(sent)
            continue
        sent['name'] = contactmanager.ContactManager(sent['peer'], saveUser=False).get_info('name')
    return json.dumps(sentbox_list)
