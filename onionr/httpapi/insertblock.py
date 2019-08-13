'''
    Onionr - Private P2P Communication

    Create blocks with the client api server
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
import json, threading
from flask import Blueprint, Response, request, g
import onionrblocks
from onionrcrypto import hashers
from onionrutils import bytesconverter
ib = Blueprint('insertblock', __name__)

@ib.route('/insertblock', methods=['POST'])
def client_api_insert_block():
    encrypt = False
    bData = request.get_json(force=True)
    message = bData['message']
    message_hash = bytesconverter.bytes_to_str(hashers.sha3_hash(message))

    # Detect if message (block body) is not specified
    if type(message) is None:
        return 'failure due to unspecified message', 400

    # Detect if block with same message is already being inserted
    if message_hash in g.too_many.get_by_string("OnionrCommunicatorDaemon").generating_blocks:
        return 'failure due to duplicate insert', 400
    else:
        g.too_many.get_by_string("OnionrCommunicatorDaemon").generating_blocks.append(message_hash)

    subject = 'temp'
    encryptType = ''
    sign = True
    meta = {}
    to = ''
    try:
        if bData['encrypt']:
            to = bData['to']
            encrypt = True
            encryptType = 'asym'
    except KeyError:
        pass
    try:
        if not bData['sign']:
            sign = False
    except KeyError:
        pass
    try:
        bType = bData['type']
    except KeyError:
        bType = 'bin'
    try:
        meta = json.loads(bData['meta'])
    except KeyError:
        pass
    threading.Thread(target=onionrblocks.insert, args=(message,), kwargs={'header': bType, 'encryptType': encryptType, 'sign':sign, 'asymPeer': to, 'meta': meta}).start()
    return Response('success')