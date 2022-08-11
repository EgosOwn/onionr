"""Onionr - Private P2P Communication.

Default example plugin for devs or to test blocks
"""
import sys
import os
import locale
from threading import Thread
from time import sleep

import cherrypy

locale.setlocale(locale.LC_ALL, '')
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# import after path insert

from utils import identifyhome
from onionrthreads import add_onionr_thread

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


plugin_name = 'rpc'
PLUGIN_VERSION = '0.0.0'
socket_file_path = identifyhome.identify_home() + 'rpc.sock'

from jsonrpc import JSONRPCResponseManager, dispatcher
import jsonrpc
import ujson
jsonrpc.manager.json = ujson

# RPC modules map Onionr APIs to the RPC dispacher
from rpc import blocks


class OnionrRPC(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def rpc(self):
        # Dispatcher is dictionary {<method_name>: callable}
        data = cherrypy.request.body.read().decode('utf-8')

        response = JSONRPCResponseManager.handle(data, dispatcher)
        return response.json


def on_init(api, data=None):
    config = {
        #'server.socket_file': socket_file_path,
        'server.socket_port': 0,
        'engine.autoreload.on': False
    }
    cherrypy.config.update(config)

    add_onionr_thread(
        cherrypy.quickstart, 5, 'OnionrRPCServer',
        OnionrRPC(), initial_sleep=0)
        