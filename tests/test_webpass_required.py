#!/usr/bin/env python3
import sys, os
import threading

from gevent import sleep
import requests

sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
import json
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

from utils import identifyhome, createdirs
from onionrsetup import setup_config
createdirs.create_dirs()
setup_config()
from onionrcommands import daemonlaunch
from onionrutils import localcommand, getclientapiserver
import config

class TestWebpass(unittest.TestCase):
    def test_needs_webpass(self):
        config.set('general.use_bootstrap', False)
        threading.Thread(target=daemonlaunch.start).start()
        while localcommand.local_command('/ping') != 'pong!':
            sleep(1)
        self.assertNotEqual(
            requests.get('http://' + getclientapiserver.get_client_API_server() + '/ping'),
            'pong!'
        )
        while True:
            try:
                daemonlaunch.kill_daemon()
            except KeyError:
                sleep(1)



unittest.main()
