"""Onionr - Private P2P Communication.

SSE API for node client access
"""
from pathlib import Path

from flask import g, Blueprint
from gevent import sleep
import gevent
import ujson

from onionrblocks.onionrblockapi import Block
from coredb.dbfiles import block_meta_db
from coredb.blockmetadb import get_block_list
from onionrutils.epoch import get_epoch
from onionrstatistics.transports.tor import TorStats
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

gevent.hub.Hub.NOT_ERROR = (gevent.GreenletExit, SystemExit, Exception)

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
    def circuit_stat_stream():
        while True:
            yield "data: " + tor_stats.get_json() + "\n\n"
            sleep(10)
    return SSEWrapper.handle_sse_request(circuit_stat_stream)

@private_sse_blueprint.route('/recentblocks')
def stream_recent_blocks():
    def _compile_json(b_list):
        js = {}
        block_obj = None
        for block in b_list:
            block_obj = Block(block)
            if block_obj.isEncrypted:
                js[block] = 'encrypted'
            else:
                js[block] = Block(block).btype
        return ujson.dumps({"blocks": js}, reject_bytes=True)

    def _stream_recent():
        last_time = Path(block_meta_db).stat().st_ctime
        while True:
            if Path(block_meta_db).stat().st_ctime != last_time:
                last_time = Path(block_meta_db).stat().st_ctime
                yield "data: " + _compile_json(get_block_list(get_epoch() - 5)) + "\n\n"
            else:
                yield "data: none" + "\n\n"
            sleep(5)
    return SSEWrapper.handle_sse_request(_stream_recent)
