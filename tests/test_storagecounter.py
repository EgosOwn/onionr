import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
from time import sleep

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
os.environ["ONIONR_HOME"] = TEST_DIR
import config
import logger
from utils import createdirs
import onionrsetup as setup
from utils import createdirs
import onionrblocks
import filepaths
import onionrexceptions
from onionrblocks import storagecounter
import onionrstorage

def _test_setup():
    TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
    print("Test directory:", TEST_DIR)
    os.environ["ONIONR_HOME"] = TEST_DIR
    createdirs.create_dirs()
    setup.setup_config()

class TestStorageCounter(unittest.TestCase):
    def test_basic_amount(self):
        _test_setup()

        self.assertIsNotNone(config.get('allocations.disk'))
        self.assertGreaterEqual(config.get('allocations.disk'), 1000000)

    def test_insert_too_much(self):
        _test_setup()
        config.set('allocations.disk', 1000)
        self.assertRaises(onionrexceptions.DiskAllocationReached, onionrblocks.insert, "test")

    def test_count(self):
        _test_setup()
        counter = storagecounter.StorageCounter()
        start_value = counter.amount
        b_hash = onionrblocks.insert("test")
        sleep(0.1)
        self.assertGreater(counter.amount, start_value)
        onionrstorage.removeblock.remove_block(b_hash)
        sleep(0.1)
        self.assertEqual(counter.amount, start_value)


unittest.main()
