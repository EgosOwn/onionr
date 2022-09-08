import dbm
import os, uuid

import time

TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
os.makedirs(TEST_DIR)

from nacl import signing

import unittest
import sys
sys.path.append('static-data/default-plugins/wot/wot')
sys.path.append("src/")
import onionrblocks
from blockdb import block_db_path
from identity import Identity
from getbykey import get_identity_by_key
from identityset import identities as iden_set
import blockdb


class GetIdentityByKeyTest(unittest.TestCase):

    def test_get_identity_by_key(self):
        iden_priv_key = signing.SigningKey.generate()
        iden_public = iden_priv_key.verify_key
        identity = Identity(iden_priv_key, "test")

        iden_set.add(identity)

        self.assertIsInstance(get_identity_by_key(iden_public), Identity)



unittest.main()
