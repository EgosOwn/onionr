from unittest.mock import patch
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from onionrcommands import parser
from onionrsetup import setup_config
setup_config()
import config
class TestToggleBootstrap(unittest.TestCase):
    def test_toggle_bootstrap(self):
        testargs = ["onionr.py", "togglebootstrap"]
        self.assertTrue(config.get('general.use_bootstrap_list'))
        with patch.object(sys, 'argv', testargs):
            parser.register()
        config.reload()
        self.assertFalse(config.get('general.use_bootstrap_list'))

unittest.main()
