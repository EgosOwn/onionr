#!/usr/bin/env python3
import sys, os
sys.path.append(".")
import unittest, uuid, sqlite3
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from urllib.request import pathname2url
import core, onionr

c = core.Core()

class OnionrTests(unittest.TestCase):
    
    def test_address_add(self):
        testAddresses = ['facebookcorewwwi.onion', '56kmnycrvepfarolhnx6t2dvmldfeyg7jdymwgjb7jjzg47u2lqw2sad.onion', '5bvb5ncnfr4dlsfriwczpzcvo65kn7fnnlnt2ln7qvhzna2xaldq.b32.i2p']
        for address in testAddresses:
            c.addAddress(address)
        dbAddresses = c.listAdders()
        for address in testAddresses:
            self.assertIn(address, dbAddresses)
        
        invalidAddresses = [None, '', '   ', '\t', '\n', ' test ', 24, 'fake.onion', 'fake.b32.i2p']
        for address in invalidAddresses:
            try:
                c.addAddress(address)
            except TypeError:
                pass
        dbAddresses = c.listAdders()
        for address in invalidAddresses:
            self.assertNotIn(address, dbAddresses) 
    
    def test_address_info(self):
        adder = 'nytimes3xbfgragh.onion'
        c.addAddress(adder)
        self.assertNotEqual(c.getAddressInfo(adder, 'success'), 1000)
        c.setAddressInfo(adder, 'success', 1000)
        self.assertEqual(c.getAddressInfo(adder, 'success'), 1000)

unittest.main()