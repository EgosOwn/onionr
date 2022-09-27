#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
from time import sleep

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs
createdirs.create_dirs()

import onionrsetup as setup
from onionrthreads import add_onionr_thread

setup.setup_config()
class OnionrThreadsTests(unittest.TestCase):

    def test_onionr_thread(self):
        l = []
        def _test_func(obj_list):
            obj_list.append(1)

        add_onionr_thread(_test_func, 0.05, "test", l, initial_sleep=0)
        sleep(0.05)
        self.assertGreaterEqual(len(l), 1)

    def test_onionr_thread_initial_sleep(self):
        l = []
        def _test_func(obj_list):
            obj_list.append(1)

        add_onionr_thread(_test_func, 0.05, "test", l, initial_sleep=1)
        sleep(0.05)
        self.assertEqual(len(l), 0)


unittest.main()
