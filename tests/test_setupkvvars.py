#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
import time
import math

from deadsimplekv import DeadSimpleKV
import setupkvvars

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
from utils import createdirs
setup.setup_config()

class SetupKVVarsTest(unittest.TestCase):
    def test_set_var_values(self):

        kv = DeadSimpleKV()
        setupkvvars.setup_kv(kv)
        self.assertEqual(kv.get('blockQueue'), {})
        self.assertFalse(kv.get('shutdown'))
        self.assertEqual(kv.get('onlinePeers'), [])
        self.assertEqual(kv.get('offlinePeers'), [])
        self.assertEqual(kv.get('peerProfiles'), [])
        self.assertEqual(kv.get('connectTimes'), {})
        self.assertEqual(kv.get('currentDownloading'), [])
        self.assertEqual(kv.get('announceCache'), {})
        self.assertEqual(kv.get('newPeers'), [])
        self.assertEqual(kv.get('dbTimestamps'), {})
        self.assertEqual(kv.get('blocksToUpload'), [])
        self.assertEqual(kv.get('cooldownPeer'), {})
        self.assertEqual(kv.get('generating_blocks'), [])
        self.assertEqual(kv.get('lastNodeSeen'), None)
        self.assertAlmostEqual(math.floor(kv.get('startTime')), math.floor(time.time()), places=0)
        self.assertTrue(kv.get('isOnline'))


unittest.main()
