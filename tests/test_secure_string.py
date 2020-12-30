#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest, json

from utils import identifyhome, createdirs
from onionrsetup import setup_config
from safedb import securestring

import filepaths
createdirs.create_dirs()
setup_config()

class TestSecureString(unittest.TestCase):
    def test_keyfile_gen(self):
        assert not os.path.exists(filepaths.secure_erase_key_file)
        securestring.generate_secure_string_key_file()
        assert os.path.exists(filepaths.secure_erase_key_file)

    def test_secure_string_encrypt(self):
        with open(filepaths.secure_erase_key_file, 'wb') as ef:
            ef.write(os.urandom(32))
        pt = "hello world"
        enc = securestring.secure_string_create(pt)
        self.assertTrue(len(enc) > len(pt))


unittest.main()
