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
from utils import createdirs
createdirs.create_dirs()
class OnionrBlockTests(unittest.TestCase):
    def test_plaintext_insert(self):
        message = 'hello world'
        onionrblocks.insert(message)

unittest.main()