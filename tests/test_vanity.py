import sys, os
sys.path.append(".")
sys.path.append("onionr/")
import unittest
import vanityonionr

import niceware

wordlist = niceware.WORD_LIST

class TestBasic(unittest.TestCase):

    def test_basic(self):
        pair = vanityonionr.find_multiprocess("onion")
        b = niceware.bytes_to_passphrase(pair[0])
        self.assertIn("onion", b)

unittest.main()