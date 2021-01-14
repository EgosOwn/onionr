"""Onionr - Private P2P Communication.

Misc client API endpoints too small to need their own file and that need access to the client api inst
"""
import os
import subprocess
import platform
from sys import stdout as sys_stdout

from flask import Response, Blueprint, request, send_from_directory, abort
from flask import g
from gevent import sleep
import unpaddedbase32

from httpapi import apiutils
import onionrcrypto
import config
from netcontroller import NetController
from onionrstatistics.serializeddata import SerializedData
from onionrutils import mnemonickeys
from onionrutils import bytesconverter
from etc import onionrvalues
from utils import reconstructhash
from utils.gettransports import get as get_tor
from .addpeer import add_peer
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

pub_key = onionrcrypto.pub_key.replace('=', '')

SCRIPT_NAME = os.path.dirname(os.path.realpath(__file__)) + \
              f'/../../../{onionrvalues.SCRIPT_NAME}'


class PrivateEndpoints:
    def __init__(self, client_api):
        private_endpoints_bp = Blueprint('privateendpoints', __name__)
        self.private_endpoints_bp = private_endpoints_bp

        @private_endpoints_bp.route('/addpeer/<name>', methods=['post'])
        def add_peer_endpoint(name):
            result = add_peer(name)
            if result == "success":
                return Response("success")
            else:
                if "already" in result:
                    return Response(result, 409)
                else:
                    return Response(result, 400)

        @private_endpoints_bp.route('/www/<path:path>', endpoint='www')
        def wwwPublic(path):
            if not config.get("www.private.run", True):
                abort(403)
            return send_from_directory(config.get('www.private.path',
                                       'static-data/www/private/'), path)

        @private_endpoints_bp.route('/getpid')
        def get_pid():
            return Response(str(os.getpid()))

        @private_endpoints_bp.route('/isatty')
        def get_is_atty():
            return Response(str(sys_stdout.isatty()).lower())

        @private_endpoints_bp.route('/hitcount')
        def get_hit_count():
            return Response(str(client_api.publicAPI.hitCount))

        @private_endpoints_bp.route('/ping')
        def ping():
            # Used to check if client api is working
            return Response("pong!")

        @private_endpoints_bp.route('/lastconnect')
        def last_connect():
            return Response(str(client_api.publicAPI.lastRequest))

        @private_endpoints_bp.route('/waitforshare/<name>', methods=['post'])
        def wait_for_share(name):
            """Prevent the **public** api from sharing blocks.

            Used for blocks we created usually
            """
            if not name.isalnum():
                raise ValueError('block hash needs to be alpha numeric')
            name = reconstructhash.reconstruct_hash(name)
            if name in client_api.publicAPI.hideBlocks:
                return Response("will be removed")
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
        def get_stats():
            """Return serialized node statistics."""
            while True:
                try:
                    return Response(client_api._too_many.get(
                        SerializedData).get_stats())
                except AttributeError:
                    pass
                except FileNotFoundError:
                    pass

        @private_endpoints_bp.route('/getuptime')
        def show_uptime():
            return Response(str(client_api.getUptime()))

        @private_endpoints_bp.route('/getActivePubkey')
        def get_active_pubkey():
            return Response(pub_key)

        @private_endpoints_bp.route('/getHumanReadable')
        def get_human_readable_default():
            return Response(mnemonickeys.get_human_readable_ID())

        @private_endpoints_bp.route('/getHumanReadable/<name>')
        def get_human_readable(name):
            name = unpaddedbase32.repad(bytesconverter.str_to_bytes(name))
            return Response(mnemonickeys.get_human_readable_ID(name))

        @private_endpoints_bp.route('/getBase32FromHumanReadable/<words>')
        def get_base32_from_human_readable(words):
            return Response(
                bytesconverter.bytes_to_str(mnemonickeys.get_base32(words)))

        @private_endpoints_bp.route('/setonboarding', methods=['POST'])
        def set_onboarding():
            return Response(
                config.onboarding.set_config_from_onboarding(request.get_json()))

        @private_endpoints_bp.route('/os')
        def get_os_system():
            return Response(platform.system().lower())

        @private_endpoints_bp.route('/gettorsocks')
        def get_tor_socks():
            while True:
                try:
                    return Response(
                        str(
                            g.too_many.get_by_string(
                                'NetController').socksPort))
                except KeyError:
                    sleep(0.1)

        @private_endpoints_bp.route('/torready')
        def is_tor_ready():
            """If Tor is starting up, the web UI is not ready to be used."""
            try:
                return Response(
                    str(g.too_many.get_by_string('NetController').readyState).lower())
            except KeyError:
                return Response("false")

        @private_endpoints_bp.route('/gettoraddress')
        def get_tor_address():
            """Return public Tor v3 Onion address for this node"""
            if not config.get('general.security_level', 0) == 0:
                abort(404)
            return Response(get_tor()[0])

        @private_endpoints_bp.route('/getgeneratingblocks')
        def get_generating_blocks() -> Response:
            return Response(
                ','.join(
                    g.too_many.get_by_string('DeadSimpleKV').get(
                        'generating_blocks'
                    ))
            )

        @private_endpoints_bp.route('/getblockstoupload')
        def get_blocks_to_upload() -> Response:
            return Response(
                ','.join(
                    g.too_many.get_by_string('DeadSimpleKV').get('blocksToUpload')
                )
            )
