"""Onionr - Private P2P Communication.

Misc public API endpoints too small to need their own file
and that need access to the public api inst
"""
from flask import Response, Blueprint, request, send_from_directory, abort, g
from . import getblocks, upload, announce
from coredb import keydb
import config
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


class PublicEndpoints:
    def __init__(self, public_api):

        public_endpoints_bp = Blueprint('publicendpoints', __name__)
        self.public_endpoints_bp = public_endpoints_bp

        @public_endpoints_bp.route('/')
        def banner():
            # Display info to people who visit a node address in their browser
            try:
                with open('../static-data/index.html', 'r') as html:
                    resp = Response(html.read(), mimetype='text/html')
            except FileNotFoundError:
                resp = Response("")
            return resp

        @public_endpoints_bp.route('/getblocklist')
        def get_block_list():
            """Get a list of blocks, optionally filtered by epoch time stamp,
            excluding those hidden"""
            return getblocks.get_public_block_list(public_api, request)

        @public_endpoints_bp.route('/getdata/<name>')
        def get_block_data(name):
            # Share data for a block if we have it and it isn't hidden
            return getblocks.get_block_data(public_api, name)

        @public_endpoints_bp.route('/www/<path:path>')
        def www_public(path):
            # A way to share files directly over your .onion
            if not config.get("www.public.run", True):
                abort(403)
            return send_from_directory(
                config.get('www.public.path', 'static-data/www/public/'), path)


        @public_endpoints_bp.route('/plaintext')
        def plaintext_enabled_endpoint():
            return Response(str(config.get("general.store_plaintext_blocks", True)).lower())

        @public_endpoints_bp.route('/ping')
        def ping():
            # Endpoint to test if nodes are up
            return Response("pong!")

        @public_endpoints_bp.route('/pex')
        def peer_exchange():
            response = ','.join(keydb.listkeys.list_adders(recent=3600))
            if len(response) == 0:
                response = ''
            return Response(response)

        @public_endpoints_bp.route('/announce', methods=['post'])
        def accept_announce():
            """Accept announcements with pow token to prevent spam"""
            g.shared_state = public_api._too_many
            resp = announce.handle_announce(request)
            return resp

        @public_endpoints_bp.route('/upload', methods=['post'])
        def upload_endpoint():
            """Accept file uploads.
            In the future this will be done more often than on creation
            to speed up block sync
            """
            return upload.accept_upload(request)
