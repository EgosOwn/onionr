#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from onionrblocks import time_insert
from onionrblocks import onionrblockapi
from onionrsetup import setup_config, setup_default_plugins
from utils import createdirs

createdirs.create_dirs()
setup_config()
setup_default_plugins()

class TestTimeInsert(unittest.TestCase):
    def test_time_insert_none(self):
        bl = time_insert('test')
        self.assertTrue(bl)
        bl = onionrblockapi.Block(bl)
        self.assertIs(bl.bmetadata['dly'], 0)

    def test_time_insert_10(self):
        bl = time_insert('test', delay=10)
        self.assertTrue(bl)
        bl = onionrblockapi.Block(bl)
        self.assertIs(bl.bmetadata['dly'], 10)

    def test_negative(self):
        self.assertRaises(ValueError, time_insert, 'test', delay=-1)
        self.assertRaises(ValueError, time_insert, 'test', delay=-10)



unittest.main()
