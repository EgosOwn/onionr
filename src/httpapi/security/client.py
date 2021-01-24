"""Onionr - Private P2P Communication.

Process incoming requests to the client api server to validate
that they are legitimate and not DNSR/XSRF or other local adversary
"""
from ipaddress import ip_address
import hmac

from flask import Blueprint, request, abort, g

from httpapi import httpheaders
from . import pluginwhitelist
import config
import logger
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

# Be extremely mindful of this.
# These are endpoints available without a password
whitelist_endpoints = [
    'www', 'staticfiles.homedata',
    'staticfiles.sharedContent',
    'staticfiles.friends', 'staticfiles.friendsindex', 'siteapi.site',
    'siteapi.siteFile', 'staticfiles.onionrhome',
    'themes.getTheme', 'staticfiles.onboarding', 'staticfiles.onboardingIndex']

remote_safe_whitelist = ['www', 'staticfiles']

public_remote_enabled = config.get('ui.public_remote_enabled', False)
public_remote_hostnames = config.get('ui.public_remote_hosts', [])


class ClientAPISecurity:
    def __init__(self, client_api):
        client_api_security_bp = Blueprint('clientapisecurity', __name__)
        self.client_api_security_bp = client_api_security_bp
        self.client_api = client_api
        pluginwhitelist.load_plugin_security_whitelist_endpoints(
            whitelist_endpoints)

        @client_api_security_bp.before_app_request
        def validate_request():
            """Validate request has set password & is the correct hostname."""
            # For the purpose of preventing DNS rebinding attacks
            if ip_address(client_api.host).is_loopback:
                localhost = True
                if request.host != '%s:%s' % \
                        (client_api.host, client_api.bindPort):
                    localhost = False

                if not localhost and public_remote_enabled:
                    if request.host not in public_remote_hostnames:
                        logger.warn(
                            f'{request.host} not in {public_remote_hostnames}')
                        abort(403)
                else:
                    if not localhost:
                        logger.warn(
                            f'Possible DNS rebinding attack by {request.host}')
                        abort(403)

            # Add shared objects
            try:
                g.too_many = self.client_api._too_many
            except KeyError:
                g.too_many = None

            # Static files for Onionr sites
            if request.path.startswith('/site/'):
                return

            if request.endpoint in whitelist_endpoints:
                return

            try:
                if not hmac.compare_digest(
                        request.headers['token'], client_api.clientToken):
                    if not hmac.compare_digest(
                            request.form['token'], client_api.clientToken):
                        abort(403)
            except KeyError:
                if not hmac.compare_digest(
                        request.form['token'], client_api.clientToken):
                    abort(403)

        @client_api_security_bp.after_app_request
        def after_req(resp):
            # Security headers
            resp = httpheaders.set_default_onionr_http_headers(resp)
            if request.endpoint in ('siteapi.site', 'siteapi.siteFile'):
                resp.headers['Content-Security-Policy'] = \
                    "default-src 'none'; style-src 'self' data: 'unsafe-inline'; img-src 'self' data:; media-src 'self' data:"  # noqa
            else:
                resp.headers['Content-Security-Policy'] = \
                    "default-src 'none'; script-src 'self'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'self'; frame-src 'none'; font-src 'self'; connect-src 'self'"  # noqa
            return resp
