#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest
from utils import identifyhome, createdirs, bettersleep
from onionrsetup import setup_config, setup_default_plugins

createdirs.create_dirs()
setup_config()
setup_default_plugins()

import kasten
from onionrblocks.generators import anonvdf
from utils import identifyhome

import safedb
import blockio

def _remove_db(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

class TestBlockIO(unittest.TestCase):
    def test_store_block(self):
        packed = kasten.generator.pack.pack(b"test", "tst")
        bl: kasten.Kasten = anonvdf.AnonVDFGenerator.generate(packed, rounds=1000)
        db_file = identifyhome.identify_home() + 'test.db'
        db = safedb.SafeDB(db_file)
        blockio.store_block(bl, db)
        db.close()
        _remove_db(db_file)

    def test_store_dupe(self):
        packed = kasten.generator.pack.pack(b"test", "tst")
        bl: kasten.Kasten = anonvdf.AnonVDFGenerator.generate(packed, rounds=1000)
        db_file = identifyhome.identify_home() + 'test.db'
        db = safedb.SafeDB(db_file)
        blockio.store_block(bl, db)
        self.assertRaises(ValueError, blockio.store_block, bl, db)
        db.close()
        _remove_db(db_file)



unittest.main()
