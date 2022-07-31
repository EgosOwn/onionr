#!/usr/bin/env python3
import sys, os
import time
import dbm
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest

from utils import createdirs
createdirs.create_dirs()


import onionrblocks

import blockdb


def _delete_db():
    try:
        os.remove(blockdb.block_db_path)
    except FileNotFoundError:
        pass

class TestBlockDBCleaner(unittest.TestCase):
    def test_clean_block_with_others(self):
        _delete_db()
        test_bl_data = b'lcRKabk1Vs(7l19baZUZ34Q\ntest'
        test_id = b'2374c534b8535a5bf35693448596c634dbea9d78a39f1519dfbcc47e8fcb25f7'.zfill(128)
        
        #onionrblocks.create_anonvdf_block()
        blockdb.add_block_to_db(onionrblocks.blockcreator.create_anonvdf_block(b"test data", b"dat", 2420))
        blockdb.add_block_to_db(onionrblocks.Block(test_id, test_bl_data, auto_verify=False))
        self.assertEqual(len(list(blockdb.get_blocks_after_timestamp(0))), 2)

        blockdb.clean_block_database()

        self.assertEqual(len(list(blockdb.get_blocks_after_timestamp(0))), 1)
    def test_clean_block_database(self):
        _delete_db()
        test_bl_data = b'lcRKabk1Vs(7l19baZUZ34Q\ntest'
        test_id = b'2374c534b8535a5bf35693448596c634dbea9d78a39f1519dfbcc47e8fcb25f7'.zfill(128)
        
        #onionrblocks.create_anonvdf_block()
        blockdb.add_block_to_db(onionrblocks.Block(test_id, test_bl_data, auto_verify=False))
        self.assertEqual(len(list(blockdb.get_blocks_after_timestamp(0))), 1)

        blockdb.clean_block_database()

        self.assertEqual(len(list(blockdb.get_blocks_after_timestamp(0))), 0)

unittest.main()
