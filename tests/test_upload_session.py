#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import hashlib
from utils import createdirs
createdirs.create_dirs()
from onionrcrypto import getourkeypair
getourkeypair.get_keypair()
from communicatorutils import uploadblocks

def hash_generator():
    hasher = hashlib.sha3_256()
    hasher.update(os.urandom(15))
    return hasher.hexdigest()

test_hashes = []
for x in range(100): test_hashes.append(hash_generator())

class UploadSessionTest(unittest.TestCase):
    def test_init_fail(self):
        s = test_hashes.pop()
        s = uploadblocks.session.UploadSession(s)
        self.assertEqual(s.total_fail_count, 0)

    def test_init_success(self):
        s = test_hashes.pop()
        s = uploadblocks.session.UploadSession(s)
        self.assertEqual(s.total_success_count, 0)

    def test_invalid(self):
        invalid = [None, 1, -1, 0, 'ab43c5b8c7b9b037d4f02fa6bc77dbb522bfcbcd7e8ea2953bf2252c6e9232a8b', lambda: None, True, False]
        for x in invalid:
            self.assertRaises((ValueError, AttributeError), uploadblocks.session.UploadSession, x)

unittest.main()
