import os, uuid
from random import randint

import secrets
from nacl import signing

TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

import unittest
import sys
sys.path.append(".")
sys.path.append('static-data/default-plugins/wot/wot/')
sys.path.append("src/")
from identity import Identity



class IdentityInitTest(unittest.TestCase):
    def test_inden_init_privkey(self):
        private_key = signing.SigningKey.generate()
        iden = Identity(private_key, "test")
        self.assertEqual(iden.name, "test")
        self.assertEqual(iden.key, private_key.verify_key)
        self.assertEqual(iden.private_key, private_key)


    def test_iden_init_pubkey(self):
        public = signing.SigningKey.generate().verify_key
        iden = Identity(public, "test")
        self.assertEqual(iden.name, "test")
        self.assertEqual(iden.key, public)
        self.assertEqual(iden.private_key, None)

    def test_iden_init_pubkey_invalid_name(self):
        public = signing.SigningKey.generate().verify_key

        self.assertRaises(ValueError, Identity, public, secrets.token_hex(32))


unittest.main()
