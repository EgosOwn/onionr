#!/usr/bin/env python3
import sys, os
sys.path.append(".")
import unittest, uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import core, onionr
from onionrutils import stringvalidators

core.Core()

class OnionrValidations(unittest.TestCase):
    
    def test_peer_validator(self):
        # Test hidden service domain validities
        valid = ['facebookcorewwwi.onion', 'vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd.onion', 
        '5bvb5ncnfr4dlsfriwczpzcvo65kn7fnnlnt2ln7qvhzna2xaldq.b32.i2p']

        invalid = [None, 'dsfewjirji0ejipdfs', '', '    ', '\n', '\r\n', 'f$ce%^okc+rewwwi.onion']

        for x in valid:
            print('testing', x)
            self.assertTrue(stringvalidators.validate_transport(x))
        
        for x in invalid:
            print('testing', x)
            self.assertFalse(stringvalidators.validate_transport(x))
    
    def test_pubkey_validator(self):
        # Test ed25519 public key validity
        valids = ['JZ5VE72GUS3C7BOHDRIYZX4B5U5EJMCMLKHLYCVBQQF3UKHYIRRQ====', 'JZ5VE72GUS3C7BOHDRIYZX4B5U5EJMCMLKHLYCVBQQF3UKHYIRRQ']
        invalid = [None, '', '    ', 'dfsg', '\n', 'JZ5VE72GUS3C7BOHDRIYZX4B5U5EJMCMLKHLYCVBQQF3UKHYIR$Q====']
        c = core.Core()

        for valid in valids:
            print('testing', valid)
            self.assertTrue(stringvalidators.validate_pub_key(valid))

        for x in invalid:
            #print('testing', x)
            self.assertFalse(stringvalidators.validate_pub_key(x))
    
    def test_integer_string(self):
        valid = ["1", "100", 100, "-5", -5]
        invalid = ['test', "1d3434", "1e100", None]

        for x in valid:
            #print('testing', x)
            self.assertTrue(stringvalidators.is_integer_string(x))   
        
        for x in invalid:
            #print('testing', x)
            self.assertFalse(stringvalidators.is_integer_string(x))
    
unittest.main()