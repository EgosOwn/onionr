#!/usr/bin/env python3
import sys, os, time, math
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
import json
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

SUCCESS_FILE = os.path.dirname(__file__) + '/runtime-result.txt'

from utils import identifyhome, createdirs
from onionrsetup import setup_config
createdirs.create_dirs()
setup_config()

class TestRuntimeFile(unittest.TestCase):
    def test_runtime_result(self):
        self.assertTrue(os.path.exists(SUCCESS_FILE))
        with open(SUCCESS_FILE, 'r') as result_file:
            self.assertLess(math.floor(time.time()) - int(result_file.read()), 3800)


unittest.main()
