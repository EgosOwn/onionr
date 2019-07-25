#!/usr/bin/env python3
import sys, os, random
sys.path.append(".")
import unittest, uuid
TEST_DIR_1 = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
TEST_DIR_2 = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
import onionr, time

import onionrexceptions, onionrcrypto as crypto
from onionrusers import onionrusers
from onionrusers import contactmanager
from utils import createdirs

class OnionrForwardSecrecyTests(unittest.TestCase):
    '''
        Tests both the onionrusers class and the contactmanager (which inherits it)
    '''

    def test_forward_encrypt(self):
        os.environ["ONIONR_HOME"] = TEST_DIR_1
        createdirs.create_dirs()
        
        friend = crypto.generate()

        friendUser = onionrusers.OnionrUser(friend[0], saveUser=True)

        for x in range(5):
            message = 'hello world %s' % (random.randint(1, 1000))
            forwardKey = friendUser.generateForwardKey()

            fakeForwardPair = crypto.generate()

            self.assertTrue(friendUser.addForwardKey(fakeForwardPair[0]))

            encrypted = friendUser.forwardEncrypt(message)

            decrypted = crypto.encryption.pub_key_decrypt(encrypted[0], privkey=fakeForwardPair[1], encodedData=True)
            self.assertEqual(decrypted, message.encode())
        return

unittest.main()