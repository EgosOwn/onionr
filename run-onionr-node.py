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
    "--skip-onboarding", help="Skip Onionr onboarding",
    type=int, default=0)
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
    type=int, default=1)
args = parser.parse_args()

p = Popen([sub_script, 'version'], stdout=DEVNULL)
p.wait()
from filepaths import config_file
from coredb import blockmetadb



with open(config_file, 'r') as cf:
    config = ujson.loads(cf.read())

if args.skip_onboarding:
    config['onboarding']['done'] = True
    print('Disabling onboarding')
if not args.random_localhost_ip:
    print('Disabling randomized localhost')
    config['general']['random_bind_ip'] = False
if not args.use_tor:
    config['transports']['tor'] = False
config['general']['display_header'] = False
config['general']['security_level'] = args.security_level

with open(config_file, 'w') as cf:
    cf.write(ujson.dumps(config))

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
