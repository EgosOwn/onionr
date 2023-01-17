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
import longrpc


plugin_apis['rpc.add_module_to_api'] = add_module_to_api


def _detect_cors_and_add_headers():
    cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
    cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
    if cherrypy.request.method == 'OPTIONS':
        return True
    return False


class OnionrRPC(object):
    @cherrypy.expose
    def threaded_rpc(self):
        if _detect_cors_and_add_headers():
            return ''

        rpc_request_json: str = cherrypy.request.body.read().decode('utf-8')
        longrpc.threaded_rpc(rpc_request_json)
        return 'ok'

    @cherrypy.expose
    def get_rpc_result(self, id=0):
        if _detect_cors_and_add_headers():
            return ''

        results = longrpc.get_results(id)
        if not results:
            return '"no result"'
        return results

    @cherrypy.expose
    def rpc(self):
        # Basic RPC, intended for small amounts of work
        # Use /queue_rpc for large workloads like creating blocks
        # and getting results with /get_rpc_result?id=<id>
        # Dispatcher is dictionary {<method_name>: callable}

        if _detect_cors_and_add_headers():
            return ''

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
    def always_fails():
        raise Exception("This always fails")
    dispatcher['ping'] = ping
    dispatcher['always_fails'] = always_fails
    pluginrpcmethods.add_plugin_rpc_methods()


def _gen_random_loopback():
    return f'127.{randbelow(256)}.{randbelow(256)}.{randbelow(256)}'


def on_setunixsocket_cmd(api, data=None):
    config.set('rpc.use_sock_file', True, savefile=True)
    logging.info('Set RPC to use unix socket')

def on_settcpsocket_cmd(api, data=None):
    config.set('rpc.use_sock_file', False, savefile=True)
    address = input('Enter address to bind to (default: random loopback): ').strip()
    if not address:
        address = _gen_random_loopback()
    port = input('Enter port to bind to (default: 0 (random/picked by OS)): ').strip()
    if not port:
        port = 0
    port = int(port)
    config.set('rpc.bind_host', address, savefile=True)
    config.set('rpc.bind_port', port, savefile=True)

    logging.info(
        'Set RPC to use TCP socket http://' +
        f'{config.get("rpc.bind_host")}:{config.get("rpc.bind_port")}')


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
