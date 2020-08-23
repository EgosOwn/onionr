#!/usr/bin/env python3

"""Craft and send requests to the local client API"""


import sys
import os
if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")

import atexit
import readline

histfile = os.path.join(os.path.expanduser("~"), ".onionr_history")
try:
    readline.read_history_file(histfile)
    # default history len is -1 (infinite), which may grow unruly
    readline.set_history_length(1000)
except FileNotFoundError:
    pass

atexit.register(readline.write_history_file, histfile)
from onionrutils.localcommand import local_command
from onionrutils.localcommand import get_hostname

try:
    print('API file found, probably running on ' + get_hostname())
except TypeError:
    print('Onionr not running')
    sys.exit(1)
print('1. get request (default)')
print('2. post request')
choice = input(">").lower().strip()
post = False
post_data = {}
json = False
endpoint = input("URL Endpoint: ")
data = input("Data url param: ")
if choice in ("2", "post", "post request"):
    post = True
    print("Enter post data")
    post_data = input()
    if post_data:
        print("Is this JSON?")
        json = input("y/n").lower().strip()
        if json == "y":
            json = True

ret = local_command(endpoint, data=data, post=post, post_data=post_data, is_json=json)
print("Response: \n", ret)
