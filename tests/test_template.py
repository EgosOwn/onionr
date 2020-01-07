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
from onionrsetup import setup_config
createdirs.create_dirs()
setup_config()

class TestTemplate(unittest.TestCase):
    '''
        Tests both the onionrusers class and the contactmanager (which inherits it)
    '''
    def test_true(self):
        self.assertTrue(True)



unittest.main()
