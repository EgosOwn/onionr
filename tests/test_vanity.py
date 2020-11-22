import sys, os
import uuid
sys.path.append(".")
sys.path.append("src/")
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest
from utils import createdirs
createdirs.create_dirs()
from onionrcrypto import getourkeypair
getourkeypair.get_keypair()
import vanityonionr

import niceware

wordlist = niceware.WORD_LIST

class TestBasic(unittest.TestCase):

    def test_basic(self):
        pair = vanityonionr.find_multiprocess("onion")
        b = niceware.bytes_to_passphrase(pair[0])
        self.assertTrue(b[0].startswith("onion"))

unittest.main()