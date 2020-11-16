#!/usr/bin/env python3

"""Enable dev default config"""

import json

conf = json.load(open('static-data/default_config.json', 'r'))

conf['tor']['use_existing_tor'] = False
conf['tor']['existing_control_port'] = 0
conf['tor']['existing_control_password'] = ""
conf['tor']['existing_socks_port'] = 0

conf['general']['dev_mode'] = False
conf['general']['insert_deniable_blocks'] = True
conf['general']['random_bind_ip'] = True
conf['general']['display_header'] = True
conf['general']['security_level'] = 0
conf['general']['use_bootstrap_list'] = True
conf['onboarding']['done'] = False
conf['general']['minimum_block_pow'] = 5
conf['general']['minimum_send_pow'] = 5
conf['log']['file']['remove_on_exit'] = True
conf['transports']['lan'] = True
conf['transports']['tor'] = True
conf['transports']['sneakernet'] = True
conf['statistics']['i_dont_want_privacy'] = False
conf['statistics']['server'] = ''
conf['ui']['animated_background'] = True

json.dump(conf, open('static-data/default_config.json', 'w'), sort_keys=True, indent=4)

