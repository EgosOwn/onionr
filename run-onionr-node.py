#!/usr/bin/env python3

import argparse
import os
from threading import Thread
from time import sleep
from subprocess import DEVNULL

import ujson
from psutil import Popen
from psutil import Process
import psutil

import sys
import curses

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(script_dir + '/src/')

from etc import onionrvalues


sub_script = script_dir + '/' + onionrvalues.SCRIPT_NAME


def show_info(p: Process):
    def pbar(window):
        window.addstr(8, 10, "Onionr statistics")
        window.addstr(9, 10, "-" * 17)
        curses.curs_set(0)
        while True:
            threads = p.num_threads()
            open_files = len(p.open_files())
            cpu_percent = p.cpu_percent()
            block_count = len(blockmetadb.get_block_list())
            for proc in p.children(recursive=True):
                threads += proc.num_threads()
                cpu_percent += proc.cpu_percent()
                try:
                    open_files += len(proc.open_files())
                except psutil.AccessDenied:
                    pass
            cpu_percent = cpu_percent * 100
            window.addstr(11, 10, f"Threads: {threads}")
            window.addstr(10, 10, f"Open files: {open_files}")
            window.addstr(12, 10, f"CPU: {cpu_percent}%")
            window.addstr(13, 10, f"Blocks: {block_count}")
            window.refresh()
            sleep(0.5)
    sleep(15)
    curses.wrapper(pbar)
    while True:
        sleep(1)


parser = argparse.ArgumentParser()

parser.add_argument(
    "--show-stats", help="Display curses output of Onionr stats",
    type=int, default=0)
parser.add_argument(
    "--onboarding", help="Use Onionr onboarding (if first load)",
    type=int, default=1)
parser.add_argument(
    "--security-level", help="Set Onionr security level",
    type=int, default=0)
parser.add_argument(
    '--open-ui', help='Open onionr web ui after started',
    type=int, default=1)
parser.add_argument(
    '--random-localhost-ip', help='bind to random localhost IP for extra security',
    type=int, default=1)
parser.add_argument(
    '--use-tor', help='Use Tor transport',
    type=int, default=1)
parser.add_argument(
    '--private-key', help='Use existing private key',
    type=str, default=0)
parser.add_argument(
    '--animated-background', help='Animated background on webui index. Just for looks.',
    type=int, default=0)
parser.add_argument(
    '--keep-log-on-exit', help='Onionr can keep or delete its log file on exit',
    type=int, default=0)
parser.add_argument(
    '--use-upload-mixing', help='Re-upload blocks uploaded to us. Slow but more secure',
    type=int, default=0)
parser.add_argument(
    '--dev-mode',
    help='Developer mode makes restarting and testing Onionr less tedious during development',
    type=int, default=0)
parser.add_argument(
    '--disable-plugin-list',
    help='plugins to disable by name, separate with commas',
    type=str, default='chat'
)
parser.add_argument(
    '--store-plaintext',
    help='store plaintext blocks or not. note that encrypted blocks may not really be encrypted, but we cannot detect that',
    type=int, default=1
)

args = parser.parse_args()

p = Popen([sub_script, 'version'], stdout=DEVNULL)
p.wait()
from filepaths import config_file, keys_file
from coredb import blockmetadb
import onionrcrypto


with open(config_file, 'r') as cf:
    config = ujson.loads(cf.read())


if args.private_key:
    priv = args.private_key
    pub = onionrcrypto.cryptoutils.get_pub_key_from_priv(priv)
    with open(keys_file, "a") as f:
        f.write(',' + pub.decode() + ',' + priv)
    config['general']['public_key'] = pub

config['plugins']['disabled'] = args.disable_plugin_list.split(',')
config['general']['dev_mode'] = False

config['general']['store_plaintext_blocks'] = True

if not args.store_plaintext:
    config['general']['store_plaintext_blocks'] = False
if args.dev_mode:
    config['general']['dev_mode'] = True
if not args.onboarding:
    config['onboarding']['done'] = True
if not args.random_localhost_ip:
    config['general']['random_bind_ip'] = False
if not args.use_tor:
    config['transports']['tor'] = False
if not args.animated_background:
    config['ui']['animated_background'] = False
if args.keep_log_on_exit:
    config['log']['file']['remove_on_exit'] = True
else:
    config['log']['file']['remove_on_exit'] = False

config['general']['upload_mixing'] = False
if args.use_upload_mixing:
    config['general']['upload_mixing'] = True
config['general']['display_header'] = False
config['general']['security_level'] = args.security_level

with open(config_file, 'w') as cf:
    cf.write(ujson.dumps(config, reject_bytes=False))

if args.open_ui:
    p = Popen([sub_script, 'start'], stdout=DEVNULL)
    sleep(2)
    Popen([sub_script, 'openhome'], stdout=DEVNULL)
else:
    p = Popen([sub_script, 'start'], stdout=DEVNULL)

p = p.children()[0]
if args.show_stats:
    Thread(target=show_info, args=[p], daemon=True).start()
p.wait()
