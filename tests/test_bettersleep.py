#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest, json

import time, math

from utils import bettersleep


class TestBetterSleep(unittest.TestCase):
    def test_better_sleep(self):
        s = math.floor(time.time())
        t = 1
        bettersleep.sleep(t)
        self.assertEqual(math.floor(time.time()) - s, t)

    def test_no_ctrl_c(self):
        # TODO: figure out how to automate ctrl-c test
        return


unittest.main()
