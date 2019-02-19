#!/usr/bin/env python3
import sys, os
sys.path.append(".")
import unittest, uuid
import json
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import core, onionr

c = core.Core()
import onionrexceptions
from onionrusers import onionrusers
from onionrusers import contactmanager

class OnionrUserTests(unittest.TestCase):
    '''
        Tests both the onionrusers class and the contactmanager (which inherits it)
    '''
    
    def test_users(self):
        keypair = c._crypto.generatePubKey()
        onionrusers.OnionrUser(c, keypair[0])
        return

    def test_contact_init_no_save(self):
        contact = c._crypto.generatePubKey()[0]
        contact = contactmanager.ContactManager(c, contact)
        self.assertFalse(contact.publicKey in c.listPeers())

    def test_contact_create(self):
        contact = c._crypto.generatePubKey()[0]
        contact = contactmanager.ContactManager(c, contact, saveUser=True)
        self.assertTrue(contact.publicKey in c.listPeers())
    
    def test_contact_set_info(self):
        contact = c._crypto.generatePubKey()[0]
        contact = contactmanager.ContactManager(c, contact, saveUser=True)
        fileLocation = '%s/contacts/%s.json' % (c.dataDir, contact.publicKey)
        contact.set_info('alias', 'bob')
        self.assertTrue(os.path.exists(fileLocation))

        with open(fileLocation, 'r') as data:
            data = data.read()
        
        data = json.loads(data)
        self.assertTrue(data['alias'] == 'bob')
    
    def test_contact_get_info(self):
        contact = c._crypto.generatePubKey()[0]
        contact = contactmanager.ContactManager(c, contact, saveUser=True)
        fileLocation = '%s/contacts/%s.json' % (c.dataDir, contact.publicKey)

        with open(fileLocation, 'w') as contactFile:
            contactFile.write('{"alias": "bob"}')
        
        self.assertTrue(contact.get_info('alias', forceReload=True) == 'bob')
        self.assertTrue(contact.get_info('fail', forceReload=True) == None)
        self.assertTrue(contact.get_info('fail') == None)
    
    def test_delete_contact(self):
        contact = c._crypto.generatePubKey()[0]
        contact = contactmanager.ContactManager(c, contact, saveUser=True)
        fileLocation = '%s/contacts/%s.json' % (c.dataDir, contact.publicKey)
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