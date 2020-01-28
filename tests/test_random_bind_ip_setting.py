import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from onionrsetup import setup_config
setup_config()
import config

class TestRandomBindIP(unittest.TestCase):
    def test_random_bind_ip_default_setting(self):
        self.assertTrue(config.get('general.random_bind_ip'))

unittest.main()
