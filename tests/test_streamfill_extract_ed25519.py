#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
import binascii
from base64 import b32decode
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest

from streamfill import extract_ed25519_from_onion_address

class TestStreamfillExtractEd25519(unittest.TestCase):
    def test_extract_normal_onion(self):
        hardcodedCorrect = b'y\xbc\xc6%\x18K\x05\x19Iu\xc2\x8bf\xb6k\x04i\xf7\xf6Uo\xb1\xac1\x89\xa7\x9b@\xdd\xa3/\x1f'
        correct = b32decode(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd'.upper())[:-3]
        self.assertEqual(correct, hardcodedCorrect)
        self.assertEqual(correct, extract_ed25519_from_onion_address('pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion'))
    def test_extract_normal_onion_bytes(self):
        hardcodedCorrect = b'y\xbc\xc6%\x18K\x05\x19Iu\xc2\x8bf\xb6k\x04i\xf7\xf6Uo\xb1\xac1\x89\xa7\x9b@\xdd\xa3/\x1f'
        correct = b32decode(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd'.upper())[:-3]
        self.assertEqual(correct, hardcodedCorrect)
        self.assertEqual(correct, extract_ed25519_from_onion_address(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion'))
    def test_extract_no_ext(self):
        hardcodedCorrect = b'y\xbc\xc6%\x18K\x05\x19Iu\xc2\x8bf\xb6k\x04i\xf7\xf6Uo\xb1\xac1\x89\xa7\x9b@\xdd\xa3/\x1f'
        correct = b32decode(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd'.upper())[:-3]
        self.assertEqual(correct, hardcodedCorrect)
        self.assertEqual(correct, extract_ed25519_from_onion_address('pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd'))
    def test_extract_no_ext_bytes(self):
        hardcodedCorrect = b'y\xbc\xc6%\x18K\x05\x19Iu\xc2\x8bf\xb6k\x04i\xf7\xf6Uo\xb1\xac1\x89\xa7\x9b@\xdd\xa3/\x1f'
        correct = b32decode(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd'.upper())[:-3]
        self.assertEqual(correct, hardcodedCorrect)
        self.assertEqual(correct, extract_ed25519_from_onion_address(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd'))
    def test_fail_length(self):
        hardcodedCorrect = b'y\xbc\xc6%\x18K\x05\x19Iu\xc2\x8bf\xb6k\x04i\xf7\xf6Uo\xb1\xac1\x89\xa7\x9b@\xdd\xa3/\x1f'
        correct = b32decode(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd'.upper())[:-3]
        self.assertEqual(correct, hardcodedCorrect)
        try:
            extract_ed25519_from_onion_address(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscry')
        except binascii.Error:
            pass
    def test_fail_length_onion(self):
        hardcodedCorrect = b'y\xbc\xc6%\x18K\x05\x19Iu\xc2\x8bf\xb6k\x04i\xf7\xf6Uo\xb1\xac1\x89\xa7\x9b@\xdd\xa3/\x1f'
        correct = b32decode(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd'.upper())[:-3]
        self.assertEqual(correct, hardcodedCorrect)
        try:
            extract_ed25519_from_onion_address(b'pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscry.onion')
        except binascii.Error:
            pass

unittest.main()
