"""Onionr - Private P2P Communication.

LAN transport server thread
"""
from gevent.pywsgi import WSGIServer
from flask import Flask
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

        @app.route("/")
        def ping():
            return "pong!"

    def start_server():
        return
