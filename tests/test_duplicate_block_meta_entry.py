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
from coredb import blockmetadb
from onionrexceptions import BlockMetaEntryExists
createdirs.create_dirs()
setup_config()

class TestDuplicateMetaEntry(unittest.TestCase):
    def test_no_duplicate(self):
        bl_hash = '0c88c7d4515363310f0a2522706c49f3f21def5f6fd69af1f91a1849239e7ea6'
        blockmetadb.add_to_block_DB(bl_hash)
        self.assertRaises(
            BlockMetaEntryExists, blockmetadb.add_to_block_DB, bl_hash)

unittest.main()
