'''
    Onionr - Private P2P Communication

    Misc client API endpoints too small to need their own file and that need access to the client api inst
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
import os
import subprocess

from flask import Response, Blueprint, request, send_from_directory, abort
import unpaddedbase32

from httpapi import apiutils
import onionrcrypto, config
from netcontroller import NetController
from serializeddata import SerializedData
from onionrutils import mnemonickeys
from onionrutils import bytesconverter
from etc import onionrvalues
from utils import reconstructhash
from onionrcommands import restartonionr

pub_key = onionrcrypto.pub_key.replace('=', '')

SCRIPT_NAME = os.path.dirname(os.path.realpath(__file__)) + f'/../../../{onionrvalues.SCRIPT_NAME}'

class PrivateEndpoints:
    def __init__(self, client_api):
        private_endpoints_bp = Blueprint('privateendpoints', __name__)
        self.private_endpoints_bp = private_endpoints_bp

        @private_endpoints_bp.route('/www/<path:path>', endpoint='www')
        def wwwPublic(path):
            if not config.get("www.private.run", True):
                abort(403)
            return send_from_directory(config.get('www.private.path', 'static-data/www/private/'), path)

        @private_endpoints_bp.route('/hitcount')
        def get_hit_count():
            return Response(str(client_api.publicAPI.hitCount))

        @private_endpoints_bp.route('/queueResponseAdd/<name>', methods=['post'])
        def queueResponseAdd(name):
            # Responses from the daemon. TODO: change to direct var access instead of http endpoint
            client_api.queueResponse[name] = request.form['data']
            return Response('success')

        @private_endpoints_bp.route('/queueResponse/<name>')
        def queueResponse(name):
            # Fetch a daemon queue response
            resp = 'failure'
            try:
                resp = client_api.queueResponse[name]
            except KeyError:
                pass
            else:
                del client_api.queueResponse[name]
            if resp == 'failure':
                return resp, 404
            else:
                return resp

        @private_endpoints_bp.route('/ping')
        def ping():
            # Used to check if client api is working
            return Response("pong!")

        @private_endpoints_bp.route('/lastconnect')
        def lastConnect():
            return Response(str(client_api.publicAPI.lastRequest))

        @private_endpoints_bp.route('/waitforshare/<name>', methods=['post'])
        def waitforshare(name):
            '''Used to prevent the **public** api from sharing blocks we just created'''
            if not name.isalnum(): raise ValueError('block hash needs to be alpha numeric')
            name = reconstructhash.reconstruct_hash(name)
            if name in client_api.publicAPI.hideBlocks:
                client_api.publicAPI.hideBlocks.remove(name)
                return Response("removed")
            else:
                client_api.publicAPI.hideBlocks.append(name)
                return Response("added")

        @private_endpoints_bp.route('/shutdown')
        def shutdown():
            return apiutils.shutdown.shutdown(client_api)

        @private_endpoints_bp.route('/restartclean')
        def restart_clean():
            subprocess.Popen([SCRIPT_NAME, 'restart'])
            return Response("bye")

        @private_endpoints_bp.route('/gethidden')
        def get_hidden_blocks():
            return Response('\n'.join(client_api.publicAPI.hideBlocks))

        @private_endpoints_bp.route('/getstats')
        def getStats():
            # returns node stats
            while True:
                try:
                    return Response(client_api._too_many.get(SerializedData).get_stats())
                except AttributeError as e:
                    pass

        @private_endpoints_bp.route('/getuptime')
        def showUptime():
            return Response(str(client_api.getUptime()))

        @private_endpoints_bp.route('/getActivePubkey')
        def getActivePubkey():
            return Response(pub_key)

        @private_endpoints_bp.route('/getHumanReadable')
        def getHumanReadableDefault():
            return Response(mnemonickeys.get_human_readable_ID())

        @private_endpoints_bp.route('/getHumanReadable/<name>')
        def getHumanReadable(name):
            name = unpaddedbase32.repad(bytesconverter.str_to_bytes(name))
            return Response(mnemonickeys.get_human_readable_ID(name))

        @private_endpoints_bp.route('/getBase32FromHumanReadable/<words>')
        def get_base32_from_human_readable(words):
            return Response(bytesconverter.bytes_to_str(mnemonickeys.get_base32(words)))

        @private_endpoints_bp.route('/gettorsocks')
        def get_tor_socks():
            return Response(str(client_api._too_many.get(NetController).socksPort))

        @private_endpoints_bp.route('/setonboarding', methods=['POST'])
        def set_onboarding():
            return Response(config.onboarding.set_config_from_onboarding(request.get_json()))

