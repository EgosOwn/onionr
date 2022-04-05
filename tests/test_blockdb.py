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

class TestBlockDB(unittest.TestCase):
    def test_store_vdf_block(self):
        _delete_db()
        bl: Block = onionrblocks.create_anonvdf_block(os.urandom(10), b'bin', 2500)
        blockdb.add_block_to_db(bl)

        with dbm.open(blockdb.block_db_path, 'r') as b_db:
            b_db[bl.id]

    def test_get_blocks_by_type(self):
        _delete_db()
        with dbm.open(blockdb.block_db_path, 'c') as b_db:
            bl: Block = onionrblocks.create_anonvdf_block('test', b'txt', 2500)
            b_db[bl.id] = bl.raw
            bl2: Block = onionrblocks.create_anonvdf_block('test2', b'bin', 2500)
            b_db[bl2.id] = bl2.raw
        looped = False
        for c, block in enumerate(blockdb.get_blocks_by_type('txt')):
            looped = True
            self.assertEqual(bl.id, block.id)
            self.assertTrue(c <= 1)
        self.assertTrue(looped)

    def test_get_blocks_after_timestamp(self):
        _delete_db()
        t = round(time.time())
        with dbm.open(blockdb.block_db_path, 'c') as b_db:
            bl: Block = onionrblocks.create_anonvdf_block('test', b'txt', 2500)
            b_db[bl.id] = bl.raw
            time.sleep(1)
            t2 = round(time.time())
            bl2: Block = onionrblocks.create_anonvdf_block('test2', b'bin', 2500)
            b_db[bl2.id] = bl2.raw

        bls = list(blockdb.get_blocks_after_timestamp(t + 10))
        self.assertTrue(len(bls) == 0)


unittest.main()
