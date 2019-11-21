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
class OnionrConfig(unittest.TestCase):
    def test_default_file(self):
        json.loads(readstatic.read_static('default_config.json'))
    
    def test_installed_config(self):
        import onionrsetup
        onionrsetup.setup_config()
        with open(TEST_DIR + 'config.json') as conf:
            json.loads(conf.read())

unittest.main()
