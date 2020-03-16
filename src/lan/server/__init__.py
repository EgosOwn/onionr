"""Onionr - Private P2P Communication.

LAN transport server thread
"""
from gevent.pywsgi import WSGIServer
from flask import Flask
from flask import Response
from gevent import sleep

from httpapi.fdsafehandler import FDSafeHandler
from netcontroller import get_open_port
import config
from coredb.blockmetadb import get_block_list
from lan.getip import lan_ips, best_ip
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


class LANServer:
    def __init__(self, shared_state):
        app = Flask(__name__)
        self.app = app
        self.host = config.get('lan.bind_ip', '')
        self.server = None
        if self.host == '':
            self.host = best_ip
        self.port = None

        @app.route('/blist/<time>')
        def get_block_list_for_lan(time):
            return Response(get_block_list(dateRec=time).split('\n'))

        @app.route("/ping")
        def ping():
            return Response("pong!")

    def start_server(self):
        self.server = WSGIServer((self.host, get_open_port()),
                                 self.app, log=None,
                                 handler_class=FDSafeHandler)
        self.port = self.server.server_port
        self.server.serve_forever()

