#!/usr/bin/env python3
import sys, os
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


class TestBlockDB(unittest.TestCase):
    def test_store_vdf_block(self):
        bl: Block = onionrblocks.create_anonvdf_block(os.urandom(10), b'bin', 2500)
        blockdb.store_vdf_block(bl)

        with dbm.open(blockdb.block_db_path, 'r') as b_db:
            b_db[bl.id]

    def test_get_blocks_by_type(self):
        with dbm.open(blockdb.block_db_path, 'c') as b_db:
            bl: Block = onionrblocks.create_anonvdf_block('test', b'txt', 2500)
            b_db[bl.id] = bl.raw
        looped = False
        for block in blockdb.get_blocks_by_type('txt'):
            looped = True
            self.assertEqual(bl.id, block.id)
        self.assertTrue(looped)



unittest.main()
