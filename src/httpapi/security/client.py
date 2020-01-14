'''
    Onionr - Private P2P Communication

    Process incoming requests to the client api server to validate they are legitimate
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
import hmac
from flask import Blueprint, request, abort, g
from onionrservices import httpheaders
from . import pluginwhitelist

# Be extremely mindful of this. These are endpoints available without a password
whitelist_endpoints = ['www', 'staticfiles.homedata', 'staticfiles.sharedContent',
'staticfiles.friends', 'staticfiles.friendsindex', 'siteapi.site', 'siteapi.siteFile', 'staticfiles.onionrhome',
'themes.getTheme', 'staticfiles.onboarding', 'staticfiles.onboardingIndex']

class ClientAPISecurity:
    def __init__(self, client_api):
        client_api_security_bp = Blueprint('clientapisecurity', __name__)
        self.client_api_security_bp = client_api_security_bp
        self.client_api = client_api
        pluginwhitelist.load_plugin_security_whitelist_endpoints(whitelist_endpoints)

        @client_api_security_bp.before_app_request
        def validate_request():
            '''Validate request has set password and is the correct hostname'''
            # For the purpose of preventing DNS rebinding attacks
            if request.host != '%s:%s' % (client_api.host, client_api.bindPort):
                abort(403)

            # Add shared objects
            try:
                g.too_many = self.client_api._too_many
            except KeyError:
                g.too_many = None

            if request.endpoint in whitelist_endpoints:
                return
            if request.path.startswith('/site/'): return

            try:
                if not hmac.compare_digest(request.headers['token'], client_api.clientToken):
                    if not hmac.compare_digest(request.form['token'], client_api.clientToken):
                        abort(403)
            except KeyError:
                if not hmac.compare_digest(request.form['token'], client_api.clientToken):
                    abort(403)

        @client_api_security_bp.after_app_request
        def after_req(resp):
            # Security headers
            resp = httpheaders.set_default_onionr_http_headers(resp)
            if request.endpoint in ('siteapi.site', 'siteapi.siteFile'):
                resp.headers['Content-Security-Policy'] = "default-src 'none'; style-src 'self' data: 'unsafe-inline'; img-src 'self' data:; media-src 'self' data:"
            else:
                resp.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'none'; frame-src 'none'; font-src 'self'; connect-src 'self'"
            return resp
