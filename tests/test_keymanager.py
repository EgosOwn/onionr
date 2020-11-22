#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs
createdirs.create_dirs()
from coredb import keydb
import onionrsetup as setup, keymanager, filepaths
from onionrutils import stringvalidators
from onionrcrypto import getourkeypair
getourkeypair.get_keypair()
setup.setup_config()
pub_key = keymanager.KeyManager().getPubkeyList()[0]
class KeyManagerTest(unittest.TestCase):
    def test_sane_default(self):
        self.assertGreaterEqual(len(pub_key), 52)
        self.assertLessEqual(len(pub_key), 56)
        self.assertEqual(pub_key, keymanager.KeyManager().getPubkeyList()[0])
        stringvalidators.validate_pub_key(pub_key)
    def test_change(self):
        new_key = keymanager.KeyManager().addKey()[0]
        self.assertNotEqual(new_key, pub_key)
        self.assertEqual(new_key, keymanager.KeyManager().getPubkeyList()[1])
        stringvalidators.validate_pub_key(new_key)
    def test_remove(self):
        manager = keymanager.KeyManager()
        new_key = manager.addKey()[0]
        priv_key = manager.getPrivkey(new_key)
        self.assertIn(new_key, manager.getPubkeyList())
        with open(filepaths.keys_file, 'r') as keyfile:
            self.assertIn(new_key, keyfile.read())
        manager.removeKey(new_key)
        with open(filepaths.keys_file, 'r') as keyfile:
            self.assertNotIn(new_key, keyfile.read())

unittest.main()
