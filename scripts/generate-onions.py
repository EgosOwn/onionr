#!/usr/bin/env python3

import sys
import os
import stem
from stem import process
from stem.control import Controller
if not os.path.exists('onionr.sh'):
    os.chdir('../')
sys.path.append("src/")

try:
    sys.argv[1]
except IndexError:
    sys.exit(1)

tor_process = process.launch_tor_with_config(
    completion_percent=0,
  config = {
    'ControlPort': '2778',
    'DisableNetwork': '1',
    'Log': [
      'NOTICE stdout',
      'ERR file /tmp/tor_error_log',
    ],
  },
)

with Controller.from_port('127.0.0.1', 2778) as controller:
    controller.authenticate()
    for i in range(1024, 1024 + int(sys.argv[1])):
        hs = controller.create_ephemeral_hidden_service(
            {80: i},
            key_type='NEW',
            key_content='ED25519-V3',
            await_publication=False,
            detached=True)
        print(hs.service_id + ".onion")
        controller.remove_ephemeral_hidden_service(hs.service_id)

tor_process.kill()