#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest, json
import dbm

from utils import identifyhome, createdirs
from onionrsetup import setup_config
createdirs.create_dirs()
setup_config()
import safedb

db_path = identifyhome.identify_home() + "test.db"

def _remove_db():
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass

class TestSafeDB(unittest.TestCase):
    def test_db_create_unprotected(self):
        _remove_db()
        db = safedb.SafeDB(db_path, protected=False)
        db.close()
        with dbm.open(db_path) as db:
            self.assertEqual(db['enc'], b'0')

    def test_db_create_protected(self):
        _remove_db()
        db = safedb.SafeDB(db_path, protected=True)
        db.close()
        with dbm.open(db_path) as db:
            self.assertEqual(db['enc'], b'1')

    def test_db_open_protected(self):
        _remove_db()
        with dbm.open(db_path, 'c') as db:
            db['enc'] = b'1'
        db = safedb.SafeDB(db_path, protected=True)
        db.close()
        self.assertRaises(safedb.DBProtectionOpeningModeError, safedb.SafeDB, db_path, protected=False)

    def test_db_open_unprotected(self):
        _remove_db()
        with dbm.open(db_path, 'c') as db:
            db['enc'] = b'0'
        db = safedb.SafeDB(db_path, protected=False)
        db.close()
        self.assertRaises(safedb.DBProtectionOpeningModeError, safedb.SafeDB, db_path, protected=True)

    def test_db_put_unprotected(self):
        _remove_db()
        db = safedb.SafeDB(db_path, protected=False)
        db.put("test", b"Test")
        db.close()
        with dbm.open(db_path, 'c') as db:
            self.assertEqual(db['test'], b"Test")

unittest.main()
