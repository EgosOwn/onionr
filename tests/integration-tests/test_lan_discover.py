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
from utils import createdirs
from onionrsetup import setup_config, setup_default_plugins
from coredb import blockmetadb
from etc.onionrvalues import BLOCK_EXPORT_FILE_EXT
from threading import Thread

createdirs.create_dirs()
setup_config()
setup_default_plugins()
import config
from filepaths import export_location

class OnionrTests(unittest.TestCase):
    def test_lan_discover(self):
        testargs = ['onionr.py', 'start']
        with patch.object(sys, 'argv', testargs):
            try:
                Thread(target=parser.register, daemon=True).start()
            except SystemExit:
                pass


unittest.main()
