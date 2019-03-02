#!/usr/bin/env python3
import sys, os, random
sys.path.append(".")
import unittest, uuid
TEST_DIR_1 = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
TEST_DIR_2 = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
import core, onionr, time

import onionrexceptions
from onionrusers import onionrusers
from onionrusers import contactmanager

class OnionrForwardSecrecyTests(unittest.TestCase):
    '''
        Tests both the onionrusers class and the contactmanager (which inherits it)
    '''

    def test_forward_encrypt(self):
        os.environ["ONIONR_HOME"] = TEST_DIR_1
        o = onionr.Onionr()
        
        friend = o.onionrCore._crypto.generatePubKey()

        friendUser = onionrusers.OnionrUser(o.onionrCore, friend[0], saveUser=True)

        for x in range(5):
            message = 'hello world %s' % (random.randint(1, 1000))
            forwardKey = friendUser.generateForwardKey()

            fakeForwardPair = o.onionrCore._crypto.generatePubKey()

            self.assertTrue(friendUser.addForwardKey(fakeForwardPair[0]))

            encrypted = friendUser.forwardEncrypt(message)

            decrypted = o.onionrCore._crypto.pubKeyDecrypt(encrypted[0], privkey=fakeForwardPair[1], encodedData=True)
            self.assertEqual(decrypted, message.encode())
        return

unittest.main()