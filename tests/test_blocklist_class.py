#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest

from utils import identifyhome, createdirs, bettersleep
from onionrsetup import setup_config, setup_default_plugins

createdirs.create_dirs()
setup_config()
setup_config()
setup_default_plugins()

import config
config.set("general.minimum_block_pow", 2)
config.set('general.minimum_send_pow', 2)
config.save()
from onionrblocks import BlockList, insert


class TestBlockList(unittest.TestCase):
    def test_block_list(self):
        block_list = BlockList()
        self.assertEqual(len(block_list.get()), 0)
        bl = insert('test')
        bettersleep.better_sleep(0.8)
        self.assertIn(bl, block_list.get())
        bl2 = insert('test2')
        bettersleep.better_sleep(0.8)
        self.assertIn(bl2, block_list.get())
        self.assertIn(bl, block_list.get())

unittest.main()
