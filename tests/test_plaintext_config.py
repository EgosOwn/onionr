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
import config
from coredb import blockmetadb
from onionrblocks.insert import insert_block

class TestTemplate(unittest.TestCase):
    def test_plaintext_config(self):
        b1 = insert_block('test block')
        self.assertIn(b1, blockmetadb.get_block_list())
        config.set('general.store_plaintext_blocks', False)
        self.assertNotIn(b1, blockmetadb.get_block_list())



unittest.main()
