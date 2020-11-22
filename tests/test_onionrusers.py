#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
import json
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs
createdirs.create_dirs()
from onionrcrypto import getourkeypair
getourkeypair.get_keypair()

import onionrexceptions
from onionrusers import onionrusers
from onionrusers import contactmanager
import onionrcrypto as crypto
from coredb import keydb
from utils import identifyhome
class OnionrUserTests(unittest.TestCase):
    '''
        Tests both the onionrusers class and the contactmanager (which inherits it)
    '''

    def test_users(self):
        keypair = crypto.generate()
        onionrusers.OnionrUser(keypair[0])

    def test_contact_init_no_save(self):
        contact = crypto.generate()[0]
        contact = contactmanager.ContactManager(contact)
        self.assertFalse(contact.publicKey in keydb.listkeys.list_peers())

    def test_contact_create(self):
        contact = crypto.generate()[0]
        contact = contactmanager.ContactManager(contact, saveUser=True)
        self.assertTrue(contact.publicKey in keydb.listkeys.list_peers())

    def test_contact_set_info(self):
        contact = crypto.generate()[0]
        contact = contactmanager.ContactManager(contact, saveUser=True)
        fileLocation = '%s/contacts/%s.json' % (identifyhome.identify_home(), contact.publicKey)
        contact.set_info('alias', 'bob')
        self.assertTrue(os.path.exists(fileLocation))

        with open(fileLocation, 'r') as data:
            data = data.read()

        data = json.loads(data)
        self.assertEqual(data['alias'], 'bob')

    def test_contact_get_info(self):
        contact = crypto.generate()[0]
        contact = contactmanager.ContactManager(contact, saveUser=True)
        fileLocation = '%s/contacts/%s.json' % (identifyhome.identify_home(), contact.publicKey)

        with open(fileLocation, 'w') as contactFile:
            contactFile.write('{"alias": "bob"}')

        self.assertEqual(contact.get_info('alias', forceReload=True), 'bob')
        self.assertEqual(contact.get_info('fail', forceReload=True), None)
        self.assertEqual(contact.get_info('fail'), None)

    def test_is_friend(self):
        contact = crypto.generate()[0]
        contact = onionrusers.OnionrUser(contact, saveUser=True)
        self.assertFalse(contact.isFriend())
        contact.setTrust(1)
        self.assertTrue(contact.isFriend())

    def test_encrypt(self):
        contactPair = crypto.generate()
        contact = contactmanager.ContactManager(contactPair[0], saveUser=True)
        encrypted = contact.encrypt('test')
        decrypted = crypto.encryption.pub_key_decrypt(encrypted, privkey=contactPair[1], encodedData=True).decode()
        self.assertEqual('test', decrypted)

    def test_delete_contact(self):
        contact = crypto.generate()[0]
        contact = contactmanager.ContactManager(contact, saveUser=True)
        fileLocation = '%s/contacts/%s.json' % (identifyhome.identify_home(), contact.publicKey)
        self.assertFalse(os.path.exists(fileLocation))
        with open(fileLocation, 'w') as contactFile:
            contactFile.write('{"alias": "test"}')
        self.assertTrue(os.path.exists(fileLocation))
        contact.delete_contact()
        self.assertFalse(os.path.exists(fileLocation))
        try:
            contact.get_info('alias')
        except onionrexceptions.ContactDeleted:
            pass
        else:
            self.assertTrue(False)
        try:
            contact.set_info('alias', 'test2')
        except onionrexceptions.ContactDeleted:
            pass
        else:
            self.assertTrue(False)

unittest.main()
