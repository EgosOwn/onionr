'''
    Onionr - Private P2P Communication

    Misc public API endpoints too small to need their own file and that need access to the public api inst
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
from flask import Response, Blueprint, request, send_from_directory, abort
from . import getblocks, upload, announce
class PublicEndpoints:
    def __init__(self, public_api):
        client_API = public_api.clientAPI
        config = client_API._core.config

        public_endpoints_bp = Blueprint('publicendpoints', __name__)
        self.public_endpoints_bp = public_endpoints_bp
        @public_endpoints_bp.route('/')
        def banner():
            # Display a bit of information to people who visit a node address in their browser
            try:
                with open('static-data/index.html', 'r') as html:
                    resp = Response(html.read(), mimetype='text/html')
            except FileNotFoundError:
                resp = Response("")
            return resp

        @public_endpoints_bp.route('/getblocklist')
        def get_block_list():
            return getblocks.public_block_list(client_API, public_api, request)

        @public_endpoints_bp.route('/getdata/<name>')
        def get_block_data(name):
            # Share data for a block if we have it
            return getblocks.public_get_block_data(client_API, public_api, name)

        @public_endpoints_bp.route('/www/<path:path>')
        def www_public(path):
            # A way to share files directly over your .onion
            if not config.get("www.public.run", True):
                abort(403)
            return send_from_directory(config.get('www.public.path', 'static-data/www/public/'), path)

        @public_endpoints_bp.route('/ping')
        def ping():
            # Endpoint to test if nodes are up
            return Response("pong!")

        @public_endpoints_bp.route('/pex')
        def peer_exchange():
            response = ','.join(client_API._core.listAdders(recent=3600))
            if len(response) == 0:
                response = ''
            return Response(response)

        @public_endpoints_bp.route('/announce', methods=['post'])
        def accept_announce():
            resp = httpapi.miscpublicapi.announce(client_API, request)
            return resp

        @public_endpoints_bp.route('/upload', methods=['post'])
        def upload():
            '''Accept file uploads. In the future this will be done more often than on creation 
            to speed up block sync
            '''
            return upload.accept_upload(client_API, request)