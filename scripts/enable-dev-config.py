#!/usr/bin/env python3

"""Enable dev default config"""

import json

input("enter to continue")  # hack to avoid vscode term input

conf = json.load(open('static-data/default_config.json', 'r'))

block_pow = int(input("Block POW level:"))

conf['general']['security_level'] = int(input("Security level:"))
conf['transports']['tor'] = False
if input('Use Tor? y/n').lower() == 'y':
    conf['transports']['tor'] = True
    if input("Reuse Tor? y/n:").lower() == 'y':
        conf['tor']['use_existing_tor'] = True
        conf['tor']['existing_control_port'] = int(input("Enter existing control port:"))
        conf['tor']['existing_control_password'] = input("Tor pass:")
        conf['tor']['existing_socks_port'] = int(input("Existing socks port:"))

conf['general']['dev_mode'] = True
conf['general']['insert_deniable_blocks'] = False
conf['general']['random_bind_ip'] = False
conf['onboarding']['done'] = True
conf['general']['minimum_block_pow'] = block_pow
conf['general']['minimum_send_pow'] = block_pow
conf['general']['use_bootstrap_list'] = False
if input("Use bootstrap list? y/n").lower() == 'y':
    conf['general']['use_bootstrap_list'] = True
conf['log']['file']['remove_on_exit'] = False
conf['ui']['animated_background'] = False
if input('Stat reporting? y/n') == 'y':
    conf['statistics']['i_dont_want_privacy'] = True
    conf['statistics']['server'] = input('Statistics server')

json.dump(conf, open('static-data/default_config.json', 'w'), sort_keys=True, indent=4)

