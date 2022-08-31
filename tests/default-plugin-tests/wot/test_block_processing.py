import os, uuid
from random import randint
from time import sleep
import secrets
import onionrblocks


TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

import unittest
import sys
sys.path.append(".")
sys.path.append('static-data/default-plugins/wot/')
sys.path.append("src/")
from wot import identity
from wot import process_block


class BlockProcessingTest(unittest.TestCase):
    def test_block_processing_trust(self):


unittest.main()
