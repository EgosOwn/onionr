from unittest.mock import patch
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
import base64
import niceware
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs
from onionrcommands import parser
import onionrsetup as setup
from utils import createdirs
from onionrsetup import setup_config, setup_default_plugins
import unpaddedbase32

createdirs.create_dirs()
setup_config()
setup_default_plugins()
import config
from filepaths import keys_file

class OnionrTests(unittest.TestCase):
    def test_vanity(self):
        testargs = ["onionr.py"]
        with patch.object(sys, 'argv', testargs):
            try:
                parser.register()
            except SystemExit:
                pass
        testargs = ["onionr.py", "add-vanity", "jolt"]
        with patch.object(sys, 'argv', testargs):
            parser.register()
        with open(keys_file, 'r') as keys:
            key_list = keys.read().split('\n')
            print('vanity key list test key database contents:', key_list)
            if not niceware.bytes_to_passphrase(unpaddedbase32.b32decode(key_list[1].split(',')[0]))[0].startswith('jolt'):
                raise ValueError('Vanity generation failed')




unittest.main()
