import sys, os
sys.path.append(".")
sys.path.append("onionr/")
import unittest, uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import filepaths
from utils import identifyhome

class TestFilePaths(unittest.TestCase):
    def test_filepaths_main(self):
        home = identifyhome.identify_home()
        self.assertTrue(filepaths.home.startswith(home))

unittest.main()
