import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid, json
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs
createdirs.create_dirs()
from onionrcrypto import getourkeypair
getourkeypair.get_keypair()
from utils import readstatic
import onionrblocks
class OnionrConfig(unittest.TestCase):
    def test_default_file(self):
        json.loads(readstatic.read_static('default_config.json'))

    def test_installed_config(self):
        import onionrsetup
        onionrsetup.setup_config()
        with open(TEST_DIR + 'config.json') as conf:
            conf = json.loads(conf.read())
            self.assertEqual(conf['advanced']['security_auditing'], True)
            self.assertEqual(conf['allocations']['disk'], 1073741824)
            self.assertEqual(conf['allocations']['disk'], 1073741824)
            self.assertEqual(conf['general']['announce_node'], True)
            self.assertEqual(conf['general']['bind_address'], '')
            self.assertEqual(conf['general']['dev_mode'], False)
            self.assertEqual(conf['general']['display_header'], True)
            self.assertEqual(conf['general']['ephemeral_tunnels'], False)
            self.assertEqual(conf['general']['hide_created_blocks'], True)
            self.assertEqual(conf['general']['insert_deniable_blocks'], True)
            self.assertEqual(conf['general']['minimum_block_pow'], 5)
            self.assertEqual(conf['general']['minimum_send_pow'], 5)
            self.assertEqual(conf['general']['public_key'], '')
            self.assertEqual(conf['general']['random_bind_ip'], True)
            self.assertEqual(conf['general']['security_level'], 0)
            self.assertEqual(conf['general']['show_notifications'], True)
            self.assertEqual(conf['general']['store_plaintext_blocks'], True)
            self.assertEqual(conf['general']['use_bootstrap_list'], True)
            self.assertEqual(conf['general']['use_subprocess_pow_if_possible'], True)
            self.assertEqual(conf['log']['console']['color'], True)
            self.assertEqual(conf['log']['console']['output'], True)
            self.assertEqual(conf['log']['file']['output'], True)
            self.assertEqual(conf['log']['file']['remove_on_exit'], True)
            self.assertEqual(conf['log']['verbosity'], 'default')
            self.assertEqual(conf['onboarding']['done'], False)
            self.assertEqual(conf['peers']['max_connect'], 1000)
            self.assertEqual(conf['peers']['max_stored_peers'], 10000000)
            self.assertEqual(conf['peers']['minimum_score'], -100)
            self.assertEqual(conf['plugins']['disabled'], [])
            self.assertEqual(conf['plugins']['enabled'], [])
            self.assertEqual(conf['timers']['getBlocks'], 10)
            self.assertEqual(conf['timers']['lookupBlocks'], 25)
            self.assertEqual(conf['tor']['bridge_fingerprint'], '')
            self.assertEqual(conf['tor']['bridge_ip'], '')
            self.assertEqual(conf['tor']['existing_control_password'], '')
            self.assertEqual(conf['tor']['existing_control_port'], 0)
            self.assertEqual(conf['tor']['existing_socks_port'], 0)
            self.assertEqual(conf['tor']['use_bridge'], False)
            self.assertEqual(conf['tor']['use_existing_tor'], False)
            self.assertEqual(conf['transports']['lan'], True)
            self.assertEqual(conf['transports']['sneakernet'], True)
            self.assertEqual(conf['transports']['tor'], True)
            self.assertEqual(conf['ui']['theme'], 'dark')
unittest.main()
