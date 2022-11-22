import tty
import sys
import subprocess

import requests
import requests_unixsocket

from logger import log as logging
import onionrplugins.pluginapis

def do_quit(): raise KeyboardInterrupt


rpc_payload = {
    "method": "echo",
    "params": ["example"],
    "jsonrpc": "2.0",
    "id": 0,
}


def list_idens():
    print('Listing identities')
    payload = dict(rpc_payload)
    payload['method'] = 'wot.serialize_identity_set'
    payload['params'].clear()
    print(onionrplugins.pluginapis.plugin_apis['rpc.rpc_client'](payload).text)



main_menu = {
    'l': (list_idens, 'list trusted identities'),
    'q': (do_quit, 'quit CLI')
}

def main_ui():
    #tty.setraw(sys.stdin)
    try:
        onionrplugins.pluginapis.plugin_apis['rpc.rpc_client']
    except KeyError:
        logging.error("Web of trust CLI requires RPC plugin to be enabled")
        return
    while True:
        # move cursor to the beginning
        print('\r', end='')
        key = sys.stdin.read(1)
        try:
            main_menu[key][0]()
        except KeyError:
            pass
        except KeyboardInterrupt:
            break


    #subprocess.Popen(['reset'], stdout=subprocess.PIPE)
