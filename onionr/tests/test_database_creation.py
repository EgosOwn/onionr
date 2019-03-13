#!/usr/bin/env python3
import sys, os
sys.path.append(".")
import unittest, uuid, sqlite3
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from urllib.request import pathname2url
import core, onionr

core.Core()

class OnionrTests(unittest.TestCase):
    
    def test_peer_db_creation(self):
        try:
            dburi = 'file:{}?mode=rw'.format(pathname2url(TEST_DIR + 'peers.db'))
            conn = sqlite3.connect(dburi, uri=True, timeout=30)
            cursor = conn.cursor()
            conn.close()
        except sqlite3.OperationalError:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

    def test_block_db_creation(self):
        try:
            dburi = 'file:{}?mode=rw'.format(pathname2url(TEST_DIR + 'blocks.db'))
            conn = sqlite3.connect(dburi, uri=True, timeout=30)
            cursor = conn.cursor()
            conn.close()
        except sqlite3.OperationalError:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

    def test_forward_keys_db_creation(self):
        try:
            dburi = 'file:{}?mode=rw'.format(pathname2url(TEST_DIR + 'forward-keys.db'))
            conn = sqlite3.connect(dburi, uri=True, timeout=30)
            cursor = conn.cursor()
            conn.close()
        except sqlite3.OperationalError:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

    def test_address_db_creation(self):
        try:
            dburi = 'file:{}?mode=rw'.format(pathname2url(TEST_DIR + 'address.db'))
            conn = sqlite3.connect(dburi, uri=True, timeout=30)
            cursor = conn.cursor()
            conn.close()
        except sqlite3.OperationalError:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

    def blacklist_db_creation(self):
        try:
            dburi = 'file:{}?mode=rw'.format(pathname2url(TEST_DIR + 'blacklist.db'))
            conn = sqlite3.connect(dburi, uri=True, timeout=30)
            cursor = conn.cursor()
            conn.close()
        except sqlite3.OperationalError:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

unittest.main()