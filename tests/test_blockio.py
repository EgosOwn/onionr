#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest
import time
from utils import identifyhome, createdirs, bettersleep
from onionrsetup import setup_config, setup_default_plugins

createdirs.create_dirs()
setup_config()
setup_default_plugins()

import kasten
from onionrblocks.generators import anonvdf
from onionrblocks import blockcreator
from utils import identifyhome

import safedb
import blockio


def _remove_db(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


class TestBlockIO(unittest.TestCase):

    def test_clean_expired(self):

        db_file = identifyhome.identify_home() + 'test.db'
        db = safedb.SafeDB(db_file)
        for i in range(3):
            bl = blockcreator.create_anonvdf_block(b"hello" + int(i).to_bytes(1, "big"), b"txt", 5)
            blockio.store_block(bl, db)
        print("done gening")
        blockio.clean_expired_blocks(db)
        time.sleep(1)
        self.assertEqual(len(list(blockio.list_blocks_by_type("txt", db))), 3)
        time.sleep(4.1)
        blockio.list_blocks_by_type("txt", db)
        db.close()
        _remove_db(db_file)

    def test_store_block(self):
        packed = kasten.generator.pack.pack(b"test", "tst")
        bl: kasten.Kasten = anonvdf.AnonVDFGenerator.generate(packed, rounds=1000)
        db_file = identifyhome.identify_home() + 'test.db'
        db = safedb.SafeDB(db_file)
        blockio.store_block(bl, db)
        db.close()
        _remove_db(db_file)

    def test_store_dupe(self):
        db_file = identifyhome.identify_home() + 'test.db'
        _remove_db(db_file)
        packed = kasten.generator.pack.pack(b"test", "tst")
        bl: kasten.Kasten = anonvdf.AnonVDFGenerator.generate(packed, rounds=1000)
        db = safedb.SafeDB(db_file)
        blockio.store_block(bl, db)
        self.assertRaises(ValueError, blockio.store_block, bl, db)
        db.close()
        _remove_db(db_file)

    def test_list_blocks(self):
        db_file = identifyhome.identify_home() + 'test.db'
        _remove_db(db_file)
        db = safedb.SafeDB(db_file)
        expected_list = []
        for i in range(10):
            bl = blockcreator.create_anonvdf_block(b'test' + int(i).to_bytes(1, 'big'), 'txt', 60)
            blockio.store_block(bl, db)
            expected_list.append(bl.id)
        #db.db_conn.sync()
        l = blockio.list_blocks_by_type('txt', db)
        self.assertEqual(len(list(l)), len(expected_list))
        for i in l:
            self.assertIn(bytes(i), expected_list)
        db.close()
        _remove_db(db_file)


unittest.main()
