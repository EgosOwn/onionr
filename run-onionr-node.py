#!/usr/bin/env python3

import argparse
import os
from threading import Thread
from time import sleep
from subprocess import PIPE

import ujson
from psutil import Popen
from psutil import Process
import psutil

import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(script_dir + '/src/')

from etc import onionrvalues


sub_script = script_dir + '/' + onionrvalues.SCRIPT_NAME

def show_info(p: Process):
    while True:
        threads = p.num_threads()
        open_files = len(p.open_files())
        for proc in p.children(recursive=True):
            threads += proc.num_threads()
            try:
                open_files += len(proc.open_files())
            except psutil.AccessDenied:
                pass
        print(f'Approximate thread count: {threads}')
        print(f'Approximate open files: {open_files}')
        sleep(1)


parser = argparse.ArgumentParser()

parser.add_argument(
    "--skip-onboarding", help="Skip Onionr onboarding",
    type=bool, default=False)
parser.add_argument(
    '--open-ui', help='Open onionr web ui after started' ,
    type=bool, default=True)
args = parser.parse_args()

p = Popen([sub_script, 'version'])
p.wait()
from filepaths import config_file



with open(config_file, 'r') as cf:
    config = ujson.loads(cf.read())

if args.skip_onboarding:
    config['onboarding']['done'] = True
    print('Disabling onboarding')


with open(config_file, 'w') as cf:
    cf.write(ujson.dumps(config))

if args.open_ui:
    p = Popen([sub_script, 'start'])
    sleep(2)
    Popen([sub_script, 'openhome'])
else:
    p = Popen([sub_script, 'start'], stdout=PIPE)

p = p.children()[0]
Thread(target=show_info, args=[p], daemon=True).start()
p.wait()
