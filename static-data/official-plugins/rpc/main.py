"""Onionr - Private P2P Communication.

Default example plugin for devs or to test blocks
"""
import sys
import os
import locale
from secrets import randbelow

import cherrypy

locale.setlocale(locale.LC_ALL, '')
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# import after path insert

from logger import log as logging
from utils import identifyhome
from onionrthreads import add_onionr_thread
import config
from onionrplugins.pluginapis import plugin_apis

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
import requests_unixsocket
import requests
jsonrpc.manager.json = ujson

from onionrplugins import plugin_apis

# RPC modules map Onionr APIs to the RPC dispacher
from rpc import blocks, pluginrpcmethods

from rpc.addmodule import add_module_to_api


plugin_apis['rpc.add_module_to_api'] = add_module_to_api

class OnionrRPC(object):
    @cherrypy.expose
    def rpc(self):
        # Dispatcher is dictionary {<method_name>: callable}
        data = cherrypy.request.body.read().decode('utf-8')

        response = JSONRPCResponseManager.handle(data, dispatcher)
        return response.json


def rpc_client(*args, **kwargs):
    if config.get('rpc.use_sock_file', True):
        session = requests_unixsocket.Session()
        return session.post(
            'http+unix://' + config.get('rpc.sock_file_path', socket_file_path).replace('/', '%2F') + '/rpc',
            *args, **kwargs)
    else:
        return requests.post(
            f'http://{config.get("rpc.bind_host")}:{config.get("rpc.bind_port")}/rpc',
            *args, **kwargs)

def on_beforecmdparsing(api, data=None):
    plugin_apis['rpc.rpc_client'] = rpc_client

def on_afterinit(api, data=None):
    def ping():
        return "pong"
    dispatcher['ping'] = ping
    pluginrpcmethods.add_plugin_rpc_methods()


def _gen_random_loopback():
    return f'127.{randbelow(256)}.{randbelow(256)}.{randbelow(256)}'


def on_init(api, data=None):
    bind_config = {}
    if config.get('rpc.use_sock_file', True, save=True):
        bind_config['server.socket_file'] = config.get(
            'rpc.sock_file_path', socket_file_path, save=True)
        # create base dir if it doesn't exist
        os.makedirs(
            os.path.dirname(config.get('rpc.sock_file_path', socket_file_path)), exist_ok=True)
    else:
        # Set default bind TCP address, if not set
        # We use a random loopback address to avoid browser side channel attacks
        # and let the OS pick a port (0)
        bind_config['server.socket_host'] = config.get(
            'rpc.bind_host', _gen_random_loopback(), save=True)
        bind_config['server.socket_port'] = config.get('rpc.bind_port', 0)
    cherrpy_config = bind_config | {
        'engine.autoreload.on': False
    }
    cherrypy.config.update(cherrpy_config)

    logging.info("Starting RPC Server")

    add_onionr_thread(
        cherrypy.quickstart, 5, 'OnionrRPCServer',
        OnionrRPC(), initial_sleep=0)
