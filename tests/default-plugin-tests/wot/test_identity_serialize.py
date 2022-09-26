import os, uuid
from random import randint

import time
from nacl import signing

TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

import unittest
import sys
sys.path.append('static-data/official-plugins/wot/wot')
sys.path.append("src/")
from identity import Identity
from identity.name import max_len


class IdentitySerializeTest(unittest.TestCase):

    def test_iden_deserialize(self):
        iden_priv_key = signing.SigningKey.generate()
        iden_public = iden_priv_key.verify_key
        serialized = iden_priv_key.sign("test".zfill(max_len).encode('utf-8') +
            bytes(iden_public) +
            str(int(time.time())).encode('utf-8'))
        iden = Identity.deserialize(serialized)
        self.assertEqual(iden.name, "test")
        self.assertEqual(iden.key, iden_public)
        self.assertEqual(iden.private_key, None)

    def test_iden_serialize(self):
        iden_priv_key = signing.SigningKey.generate()
        iden_public = iden_priv_key.verify_key
        # Onionr keys sign themselves + the date
        # in order to prevent replay attacks
        expected_serialized = \
            iden_priv_key.sign("test".zfill(max_len).encode('utf-8') +
            bytes(iden_public) +
            str(int(time.time())).encode('utf-8'))
        expected_serialized_len = len(expected_serialized)

        identity = Identity(iden_priv_key, "test")
        serialized = identity.serialize()
        print(serialized)
        self.assertEqual(len(serialized), expected_serialized_len)
        self.assertEqual(serialized, expected_serialized)

unittest.main()
