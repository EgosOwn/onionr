'''
    Onionr - Private P2P Communication

    view and interact with onionr sites
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
import base64
import binascii

import unpaddedbase32

from flask import Blueprint, Response, request, abort

from onionrblocks import onionrblockapi
import onionrexceptions
from onionrutils import stringvalidators
from utils import safezip
from onionrutils import mnemonickeys

site_api = Blueprint('siteapi', __name__)

@site_api.route('/site/<name>', endpoint='site')
def site(name):
    bHash = name
    resp = 'Not Found'
    if '-' in name:
        name = mnemonickeys.get_base32(name)
    if stringvalidators.validate_pub_key(name):
        name = unpaddedbase32.repad(name)
        

    if stringvalidators.validate_hash(bHash):
        try:
            resp = onionrblockapi.Block(bHash).bcontent
        except onionrexceptions.NoDataAvailable:
            abort(404)
        except TypeError:
            pass
        try:
            resp = base64.b64decode(resp)
        except binascii.Error:
            pass
    if resp == 'Not Found' or not resp:
        abort(404)
    return Response(resp)
