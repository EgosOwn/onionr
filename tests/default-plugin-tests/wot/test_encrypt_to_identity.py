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
import onionrblocks
from blockdb import block_db_path
import nacl.public
import nacl.exceptions
import nacl.signing
import result

import wot
from wot.identity import Identity

from wot import crypto

import blockdb


class TestEncryptToIdentity(unittest.TestCase):

    def test_encrypt_to_identity_bytes(self):
        iden_priv_key = signing.SigningKey.generate()
        iden_public = iden_priv_key.verify_key
        identity = Identity(iden_priv_key, "us")

        their_priv_key = signing.SigningKey.generate()
        their_public = their_priv_key.verify_key
        their_identity = Identity(their_priv_key, "them")

        test_message = b"test message"

        encrypted = crypto.encryption.encrypt_to_identity(identity, their_identity, test_message)
        self.assertIsInstance(encrypted, result.Ok)

        decrypted = nacl.public.Box(their_priv_key.to_curve25519_private_key(), iden_public.to_curve25519_public_key()).decrypt(encrypted.value)
        self.assertEqual(decrypted, test_message)

    def test_encrypt_to_identity_str(self):
        iden_priv_key = signing.SigningKey.generate()
        iden_public = iden_priv_key.verify_key
        identity = Identity(iden_priv_key, "us")

        their_priv_key = signing.SigningKey.generate()
        their_public = their_priv_key.verify_key
        their_identity = Identity(their_priv_key, "them")

        test_message = "test message"

        encrypted = crypto.encryption.encrypt_to_identity(identity, their_identity, test_message)
        self.assertIsInstance(encrypted, result.Ok)
        decrypted = nacl.public.Box(their_priv_key.to_curve25519_private_key(), iden_public.to_curve25519_public_key()).decrypt(encrypted.value)
        self.assertEqual(decrypted, test_message.encode('utf-8'))

    def test_encrypt_to_identity_bytes_invalid(self):
        iden_priv_key = signing.SigningKey.generate()
        iden_public = iden_priv_key.verify_key
        identity = Identity(iden_priv_key, "us")

        their_priv_key = signing.SigningKey.generate()
        their_public = their_priv_key.verify_key
        their_identity = Identity(their_priv_key, "them")

        test_message = b"test message"

        encrypted = crypto.encryption.encrypt_to_identity(identity, their_identity, test_message)
        self.assertIsInstance(encrypted, result.Ok)
        encrypted = encrypted.value[:-1] + b'\x00'
        try:
            decrypted = nacl.public.Box(their_priv_key.to_curve25519_private_key(), iden_public.to_curve25519_public_key()).decrypt(encrypted)
        except nacl.exceptions.CryptoError:
            pass
        else:
            self.fail("Decrypted invalid message")


unittest.main()
