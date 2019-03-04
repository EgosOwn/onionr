'''
    Onionr - P2P Anonymous Storage Network

    HTTP endpoints for mail plugin.
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
import sys, os, json
from flask import Response, request, redirect, Blueprint, abort
import core
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import loadinbox, sentboxdb

flask_blueprint = Blueprint('mail', __name__)
c = core.Core()
kv = c.keyStore

@flask_blueprint.route('/mail/deletemsg/<block>', methods=['POST'])
def mail_delete(block):
    if not c._utils.validateHash(block):
        abort(504)
    existing = kv.get('deleted_mail')
    if existing is None:
        existing = []
    if block not in existing:
        existing.append(block)
    kv.put('deleted_mail', existing)
    return 'success'

@flask_blueprint.route('/mail/getinbox')
def list_inbox():
    return ','.join(loadinbox.load_inbox(c))

@flask_blueprint.route('/mail/getsentbox')
def list_sentbox():
    sentbox_list = sentboxdb.SentBox(c).listSent()
    sentbox_list_copy = list(sentbox_list)
    deleted = kv.get('deleted_mail')
    if deleted is None:
        deleted = []
    for x in range(len(sentbox_list_copy)):
        if sentbox_list_copy[x]['hash'] in deleted:
            x -= 1
            sentbox_list.pop(x)

    return json.dumps(sentbox_list)