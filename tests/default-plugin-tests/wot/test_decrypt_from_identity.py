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
sys.path.append('static-data/official-plugins/wot/')
sys.path.append("src/")

import nacl.public
import nacl.exceptions
import nacl.signing
import result

import wot
from wot.identity import Identity

from wot import crypto



class TestDecryptFromIdentity(unittest.TestCase):

    def test_decrypt_from_identity(self):
        iden_priv_key = signing.SigningKey.generate()
        iden_public = iden_priv_key.verify_key
        identity = Identity(iden_priv_key, "us")

        their_priv_key = signing.SigningKey.generate()
        their_public = their_priv_key.verify_key
        their_identity = Identity(their_priv_key, "them")

        test_message = b"test message"

        encrypted = nacl.public.Box(their_priv_key.to_curve25519_private_key(), iden_public.to_curve25519_public_key()).encrypt(test_message)
        self.assertIsInstance(encrypted, bytes)

        decrypted = crypto.encryption.decrypt_from_identity(identity, their_identity, encrypted)
        self.assertIsInstance(decrypted, result.Ok)
        self.assertEqual(decrypted.value, test_message)



unittest.main()
