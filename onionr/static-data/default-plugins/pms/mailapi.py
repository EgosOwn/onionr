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
import sys, os
from flask import Response, request, redirect, Blueprint
import core
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import loadinbox

flask_blueprint = Blueprint('mail', __name__)
c = core.Core()
kv = c.keyStore

@flask_blueprint.route('/mail/deletemsg/<block>', methods=['POST'])
def mail_delete(block):
    assert c._utils.validateHash(block)
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