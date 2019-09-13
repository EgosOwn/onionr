from unittest.mock import patch
import sys, os
sys.path.append(".")
sys.path.append("onionr/")
import unittest, uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from onionrcommands import parser
class OnionrTests(unittest.TestCase):
    def test_no_command(self):
        testargs = ["onionr.py"]
        with patch.object(sys, 'argv', testargs):
            parser.register()
    def test_version_command(self):
        testargs = ["onionr.py", "version"]
        with patch.object(sys, 'argv', testargs):
            parser.register()

unittest.main()
