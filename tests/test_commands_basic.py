from unittest.mock import patch
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs
from onionrcommands import parser
import onionrsetup as setup
from netcontroller.torcontrol import customtorrc
class OnionrTests(unittest.TestCase):
    def test_version_command(self):
        testargs = ["onionr.py", "version"]
        with patch.object(sys, 'argv', testargs):
            parser.register()
    def test_site_list(self):
        createdirs.create_dirs()
        setup.setup_config()
        testargs = ["onionr.py", "list-sites"]
        with patch.object(sys, 'argv', testargs):
            parser.register()

unittest.main()
