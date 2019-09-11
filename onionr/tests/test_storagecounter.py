import sys, os
sys.path.append(".")
import unittest, uuid

import logger
from utils import createdirs
import onionrsetup as setup
from utils import createdirs
import onionrblocks
import filepaths
import onionrexceptions
import storagecounter
import onionrstorage

def _test_setup():
    import config
    TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
    print("Test directory:", TEST_DIR)
    os.environ["ONIONR_HOME"] = TEST_DIR
    createdirs.create_dirs()
    setup.setup_config()
    config.reload()

class TestStorageCounter(unittest.TestCase):
    def test_basic_amount(self):
        import config
        _test_setup()
        self.assertIsNotNone(config.get('allocations.disk'))
        self.assertGreater(config.get('allocations.disk'), 1000000)
    
    def test_insert_too_much(self):
        import config
        _test_setup()
        config.set('allocations.disk', 1000)
        self.assertRaises(onionrexceptions.DiskAllocationReached, onionrblocks.insert, "test")

    def test_count(self):
        _test_setup()
        counter = storagecounter.StorageCounter()
        start_value = counter.get_amount()
        b_hash = onionrblocks.insert("test")
        self.assertGreater(counter.get_amount(), start_value)
        onionrstorage.removeblock.remove_block(b_hash)
        self.assertEqual(counter.get_amount(), start_value)
    

unittest.main()