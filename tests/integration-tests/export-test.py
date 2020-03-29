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

createdirs.create_dirs()
setup_config()
setup_default_plugins()
import config
from filepaths import export_location

class OnionrTests(unittest.TestCase):
    def test_export(self):
        testargs = ["onionr.py", "circlesend", "tests", "hello"]
        with patch.object(sys, 'argv', testargs):
            try:
                parser.register()
            except SystemExit:
                pass
        bl = blockmetadb.get_block_list()[0]
        testargs = ["onionr.py", "export-block", bl]
        with patch.object(sys, 'argv', testargs):
            parser.register()

        with open(export_location + '/' + bl + BLOCK_EXPORT_FILE_EXT, 'rb') as f:

            if b'hello' not in f.read():
                raise ValueError('No exported block')


unittest.main()
