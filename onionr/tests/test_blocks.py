#!/usr/bin/env python3
import sys, os
sys.path.append(".")
import unittest, uuid, hashlib
import nacl.exceptions
import nacl.signing, nacl.hash, nacl.encoding
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import onionrblocks
import onionrstorage
from utils import createdirs
from onionrutils import bytesconverter
createdirs.create_dirs()
class OnionrBlockTests(unittest.TestCase):
    def test_plaintext_insert(self):
        message = 'hello world'
        bl = onionrblocks.insert(message)
        self.assertIn(bytesconverter.str_to_bytes(message), onionrstorage.getData(bl))
    
    #def test_encrypted_insert(self):
    #    key_pair_1 = nacl.signing.SigningKey.generate(encoder=nacl.encoding.base32)

unittest.main()