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
import subprocess
from nacl.secret import SecretBox

import filepaths
createdirs.create_dirs()
setup_config()


_rinseoff = f"{filepaths.app_root}/src/rinseoff/rinseoffcli"

class TestSecureString(unittest.TestCase):
    def test_keyfile_gen(self):
        assert not os.path.exists(filepaths.secure_erase_key_file)
        securestring.generate_key_file()
        assert os.path.exists(filepaths.secure_erase_key_file)

    def test_protect_string(self):
        with open(filepaths.secure_erase_key_file, 'wb') as ef:
            ef.write(os.urandom(32))
        pt = "hello world"
        enc = securestring.protect_string(pt)
        self.assertTrue(len(enc) > len(pt))

    def test_unprotect_string(self):
        key = os.urandom(32)
        with open(filepaths.secure_erase_key_file, 'wb') as ef:
            ef.write(key)
        msg = b"test hello world"
        box = SecretBox(key)
        enc = box.encrypt(msg)
        nonce = enc.nonce
        enc = nonce + enc.ciphertext
        p = subprocess.Popen(
                            ["dotnet", "run",
                                "--project", _rinseoff,
                                "load", "stdin", f"{filepaths.secure_erase_key_file}"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
        res = p.communicate(enc)
        self.assertTrue(res[0] == msg)


unittest.main()
