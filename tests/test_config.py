import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid, json
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import onionrblocks
from utils import createdirs
from utils import readstatic
createdirs.create_dirs()
class OnionrConfigTest(unittest.TestCase):
    def test_security_value(self):
        return

unittest.main()
