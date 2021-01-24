#!/usr/bin/env python3

"""Craft and send requests to the local client API"""


import sys
import os
import time
from threading import Thread
if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")

import filepaths
import config
config.reload()

with open(filepaths.private_API_host_file, 'r') as host:
    hostname = host.read()

port = config.get("client.client.port", 0)
if not port:
    print("Could not get port for Onionr UI. Try again")
    sys.exit(1)
torrc = f"""
HiddenServiceDir remote-onionr-hs
HiddenServicePort 80 {hostname}:{port}
"""

with open("remote-onionr-torrc", "w") as torrc_f:
    torrc_f.write(torrc)


def show_onion():
    while True:
        time.sleep(1)
        try:
            with open("remote-onionr-hs/hostname", "r") as f:
                o = f.read()
                print("UI Onion (Keep secret):", o)
                config.set("ui.public_remote_enabled", True)
                config.set("ui.public_remote_hosts", [o])
                config.save()
            break
        except FileNotFoundError:
            pass

Thread(target=show_onion, daemon=True).start()

os.system("tor -f remote-onionr-torrc")
