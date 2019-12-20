"""Onionr - Private P2P Communication.

This file handles all incoming http requests
to the public api server, using Flask
"""
import time
import threading
import flask
from gevent.pywsgi import WSGIServer
from httpapi import apiutils, security, fdsafehandler, miscpublicapi
import logger
import config
import filepaths
from utils import gettransports
from etc import onionrvalues, waitforsetvar
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


def _get_tor_adder(pub_api):
    transports = []
    while len(transports) == 0:
        transports = gettransports.get()
        time.sleep(0.3)
    pub_api.torAdder = transports[0]


class PublicAPI:
    """The new client api server, isolated from the public api."""

    def __init__(self):
        """Setup the public api app."""
        app = flask.Flask('PublicAPI')
        app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
        self.i2pEnabled = config.get('i2p.host', False)
        self.hideBlocks = []  # Blocks to be denied sharing
        self.host = apiutils.setbindip.set_bind_IP(
            filepaths.public_API_host_file)

        threading.Thread(target=_get_tor_adder,
                         args=[self], daemon=True).start()

        self.torAdder = ""
        self.bindPort = config.get('client.public.port')
        self.lastRequest = 0
        # total rec requests to public api since server started
        self.hitCount = 0
        self.config = config
        self.API_VERSION = onionrvalues.API_VERSION
        logger.info('Running public api on %s:%s' % (self.host, self.bindPort))

        app.register_blueprint(
            security.public.PublicAPISecurity(self).public_api_security_bp)
        app.register_blueprint(
            miscpublicapi.endpoints.PublicEndpoints(self).public_endpoints_bp)
        self.app = app

    def start(self):
        """Start the Public API server."""
        waitforsetvar.wait_for_set_var(self, "_too_many")
        self.httpServer = WSGIServer((self.host, self.bindPort),
                                     self.app, log=None,
                                     handler_class=fdsafehandler.FDSafeHandler)
        self.httpServer.serve_forever()
