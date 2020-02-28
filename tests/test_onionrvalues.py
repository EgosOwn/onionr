#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
import json
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

from utils import identifyhome, createdirs
from etc import onionrvalues

class TestOnionrValues(unittest.TestCase):
    def test_default_expire(self):
        self.assertEqual(onionrvalues.DEFAULT_EXPIRE, 2678400)


unittest.main()
