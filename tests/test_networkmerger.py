#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

from utils import createdirs
createdirs.create_dirs()
from onionrcrypto import getourkeypair
getourkeypair.get_keypair()
from utils import networkmerger
from coredb import keydb
import onionrsetup as setup
setup.setup_config()
class NetworkMergerTest(unittest.TestCase):
    def test_valid_merge(self):
        adders = 'facebookcorewwwi.onion,mporbyyjhmz2c62shctbi3ngrslne5lpcyav6uzhxok45iblodhgjoad.onion'
        networkmerger.mergeAdders(adders)
        added = keydb.listkeys.list_adders()
        self.assertIn('mporbyyjhmz2c62shctbi3ngrslne5lpcyav6uzhxok45iblodhgjoad.onion', added)
        self.assertNotIn('inwalidkcorewwi.onion', added)
        self.assertIn('facebookcorewwwi.onion', added)

    def test_invalid_mergeself(self):
        adders = 'facebookc0rewwi.onion,sdfsdfsdf.onion, ssdf324, null, \n'
        networkmerger.mergeAdders(adders)
        added = keydb.listkeys.list_adders()
        for adder in adders:
            self.assertNotIn(adder, added)

unittest.main()
