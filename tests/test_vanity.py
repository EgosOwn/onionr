import sys, os
sys.path.append(".")
sys.path.append("onionr/")
import unittest
import vanityonionr

import mnemonic
m = mnemonic.Mnemonic("english")
wordlist = m.wordlist

class TestBasic(unittest.TestCase):

    def test_basic(self):
        pair = vanityonionr.find_multiprocess("onion")
        b = m.to_mnemonic(pair[0])
        self.assertIn("onion", b)

unittest.main()