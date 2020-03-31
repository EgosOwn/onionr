#!/usr/bin/env python3
"""Onionr - Private P2P Communication.

LAN transport server thread
"""
import sys
import os
os.chdir('../')
sys.path.append("src/")
from gevent.pywsgi import WSGIServer
from flask import Flask
from flask import Response
from flask import request
import stem
from stem.control import Controller
from netcontroller import getopenport
import json
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

#passw = secrets.token_hex(32)
port_num = int(input('tor control port'))
web_port = getopenport.get_open_port()


app = Flask(__name__)

STATS_FILE = 'stats.json'

@app.route('/sendstats/<node>', methods = ['POST'])
def get_stats(node):
    try:
        with open(STATS_FILE, 'r') as f:
            try:
                data = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                raise FileNotFoundError
    except FileNotFoundError:
        data = {}
    data[node] = request.get_data().decode('utf-8')

    with open(STATS_FILE, 'w') as f:
        data = json.dumps(data)
        f.write(data)

    return Response('ok')

with Controller.from_port(port = port_num) as controller:
    controller.authenticate(input('pass for tor'))  # provide the password here if you set one
    hs = controller.create_ephemeral_hidden_service(
            {80: web_port},
            key_type = 'NEW',
            key_content = 'ED25519-V3',
            await_publication=True,
            detached=True)
    hs = hs.service_id
    print(f'stats server {hs}')

    server = WSGIServer(('127.0.0.1', web_port), app, log=None)
    server.serve_forever()

