"""Onionr - Private P2P Communication.

view and interact with onionr sites
"""
import base64
import binascii
import mimetypes

import unpaddedbase32

from flask import Blueprint, Response, request, abort

from onionrblocks import onionrblockapi
import onionrexceptions
from onionrutils import stringvalidators
from onionrutils import mnemonickeys
from . import sitefiles
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


site_api = Blueprint('siteapi', __name__)

@site_api.route('/site/<name>/', endpoint='site')
def site(name: str)->Response:
    """Accept a site 'name', if pubkey then show multi-page site, if hash show single page site"""
    resp: str = 'Not Found'
    mime_type = 'text/html'

    # If necessary convert the name to base32 from mnemonic
    if mnemonickeys.DELIMITER in name:
        name = mnemonickeys.get_base32(name)

    # Now make sure the key is regardless a valid base32 format ed25519 key (readding padding if necessary)
    if stringvalidators.validate_pub_key(name):
        name = unpaddedbase32.repad(name)
        resp = sitefiles.get_file(name, 'index.html')

    elif stringvalidators.validate_hash(name):
        try:
            resp = onionrblockapi.Block(name).bcontent
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

@site_api.route('/site/<name>/<path:file>', endpoint='siteFile')
def site_file(name: str, file: str)->Response:
    """Accept a site 'name', if pubkey then show multi-page site, if hash show single page site"""
    resp: str = 'Not Found'
    mime_type = mimetypes.MimeTypes().guess_type(file)[0]

    # If necessary convert the name to base32 from mnemonic
    if mnemonickeys.DELIMITER in name:
        name = mnemonickeys.get_base32(name)

    # Now make sure the key is regardless a valid base32 format ed25519 key (readding padding if necessary)
    if stringvalidators.validate_pub_key(name):
        name = unpaddedbase32.repad(name)
        resp = sitefiles.get_file(name, file)

    elif stringvalidators.validate_hash(name):
        try:
            resp = onionrblockapi.Block(name).bcontent
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
    return Response(resp, mimetype=mime_type)
