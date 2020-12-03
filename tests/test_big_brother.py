import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid

import requests

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs, identifyhome
import onionrsetup as setup
import onionrexceptions


createdirs.create_dirs()
setup.setup_config()

class TestBigBrother(unittest.TestCase):
    def test_requests_connect(self):
        import bigbrother
        bigbrother.enable_ministries()
        with self.assertRaises(onionrexceptions.NetworkLeak):
            requests.get('https://example.com')
        with self.assertRaises(onionrexceptions.NetworkLeak):
            requests.get('https://1.1.1.1/')


unittest.main()
