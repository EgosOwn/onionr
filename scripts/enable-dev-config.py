#!/usr/bin/env python3

"""Enable dev default config"""

import json

conf = json.load(open('static-data/default_config.json', 'r'))

if input("Reuse Tor? y/n:").lower() == 'y':
    conf['tor']['use_existing_tor'] = True
    conf['tor']['existing_control_port'] = int(input("Enter existing control port:"))
    conf['tor']['existing_control_password'] = input("Tor pass:")
    conf['tor']['existing_socks_port'] = int(input("Existing socks port:"))

conf['general']['dev_mode'] = True
conf['general']['insert_deniable_blocks'] = False
conf['general']['random_bind_ip'] = False
conf['onboarding']['done'] = True
conf['general']['minimum_block_pow'] = 4
conf['general']['minimum_send_pow'] = 4

json.dump(conf, open('static-data/default_config.json', 'w'), sort_keys=True, indent=4)

