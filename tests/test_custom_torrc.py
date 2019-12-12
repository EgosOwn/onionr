import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs, identifyhome
import onionrsetup as setup
from netcontroller.torcontrol import customtorrc
createdirs.create_dirs()
setup.setup_config()

class TestCustomTorrc(unittest.TestCase):
    def test_torrc_get(self):
        torrc = identifyhome.identify_home() + '/torrc-custom'
        self.assertEqual(customtorrc.get_custom_torrc(), '\n')
        with open(torrc, 'w') as torrc_file:
            torrc_file.write('test')
        self.assertEqual(customtorrc.get_custom_torrc(), '\ntest')
        os.remove(torrc)

    def test_torrc_set(self):
        torrc = identifyhome.identify_home() + '/torrc-custom'
        customtorrc.set_custom_torrc('test2')
        with open(torrc, 'r') as torrc_file:
            self.assertEqual(torrc_file.read().splitlines()[2], 'test2')
        os.remove(torrc)

unittest.main()
