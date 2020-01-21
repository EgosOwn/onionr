"""Onionr - Private P2P Communication.

SSE API for node client access
"""
from flask import g, Blueprint
from gevent import sleep

from statistics.transports.tor import TorStats
from .. import wrapper
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

private_sse_blueprint = Blueprint('privatesse', __name__)
SSEWrapper = wrapper.SSEWrapper()


@private_sse_blueprint.route('/hello')
def stream_hello():
    def print_hello():
        while True:
            yield "hello\n\n"
            sleep(1)
    return SSEWrapper.handle_sse_request(print_hello)


@private_sse_blueprint.route('/torcircuits')
def stream_tor_circuits():
    tor_stats = g.too_many.get(TorStats)
    def stream():
        while True:
            yield tor_stats.get_json()

            sleep(3)
    return SSEWrapper.handle_sse_request(stream)
