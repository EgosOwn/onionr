import tty
import sys
import subprocess
import traceback

import ujson as json
import result
import requests
import requests_unixsocket

from logger import log as logging
import onionrplugins.pluginapis

from .trustidentity import trust_identity

def do_quit(): raise KeyboardInterrupt


rpc_payload_template = {
    "method": "echo",
    "params": ["example"],
    "jsonrpc": "2.0",
    "id": 0,
}


def list_idens():
    print('Listing identities')
    payload = dict(rpc_payload_template)
    payload['method'] = 'wot.serialize_identity_set'
    del payload['params']
    print(onionrplugins.pluginapis.plugin_apis['rpc.rpc_client'](json=payload).text)


def ping_api() -> result.Result:
    payload = dict(rpc_payload_template)
    payload['method'] = 'ping'
    del payload['params']
    try:
        _ping_res = onionrplugins.pluginapis.plugin_apis['rpc.rpc_client'](json=payload).text
    except requests.exceptions.ConnectionError:
        logging.debug(traceback.format_exc())
        return result.Err('Could not connect to Onionr RPC server. Please ensure the RPC plugin is enabled and the Onionr daemon is running')
    except:
        logging.error(traceback.format_exc())
        return result.Err('Unknown error occurred while connecting to Onionr RPC server')
    _ping_res = json.loads(_ping_res)
    if _ping_res['result'] == 'pong':
        return result.Ok()
    else:
        return result.Err('API not responding. Try restarting Onionr')


main_menu = {
    'l': (list_idens, 'list trusted identities'),
    't': (trust_identity, 'trust identity'),
    'q': (do_quit, 'quit CLI')
}

def main_ui():
    #tty.setraw(sys.stdin)
    try:
        onionrplugins.pluginapis.plugin_apis['rpc.rpc_client']
    except KeyError:
        logging.error("Web of trust CLI requires RPC plugin to be enabled")
        return

    ping_result: result.Result = ping_api()
    if not isinstance(ping_result, result.Ok):
        logging.error(ping_result)
        return

    while True:
        # move cursor to the beginning
        print('\r', end='')
        try:
            key = sys.stdin.read(1)
            main_menu[key][0]()
        except KeyError:
            pass
        except KeyboardInterrupt:
            break


    #subprocess.Popen(['reset'], stdout=subprocess.PIPE)
