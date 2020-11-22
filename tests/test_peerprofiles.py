import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
import base64

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs
createdirs.create_dirs()
from onionrcrypto import getourkeypair
getourkeypair.get_keypair()
from onionrpeers import peerprofiles
import onionrexceptions
from coredb import keydb
from onionrutils import stringvalidators, epoch
TEST_PEER = '3n5wclq4w4pfkcfmjcpqrjluctpm2tzt7etfblavf42cntv6hrerkzyb.onion'

def rand_fake_adder_generator():
    rand_bytes = os.urandom(35)
    return base64.b32encode(rand_bytes).decode().lower() + '.onion'

test_peers = []
for x in range(100):
    p = rand_fake_adder_generator()
    assert stringvalidators.validate_transport(p)
    test_peers.append(p)

class TestPeerProfiles(unittest.TestCase):
    def test_invalid_init(self):
        self.assertRaises(onionrexceptions.InvalidAddress, peerprofiles.PeerProfiles, "invalid")
    def test_valid_init(self):
        peerprofiles.PeerProfiles(test_peers.pop())

    def test_load_score(self):
        p = peerprofiles.PeerProfiles(test_peers.pop())
        self.assertEqual(p.score, 0)

    def test_inc_score(self):
        p = peerprofiles.PeerProfiles(test_peers.pop())
        s = 0
        for x in range(2):
            s += 1
            p.addScore(1)
            self.assertEqual(p.score, s)

    def test_inc_score_with_db(self):
        p = peerprofiles.PeerProfiles(test_peers.pop())
        s = 0
        for x in range(2):
            p.last_updated['score'] = epoch.get_epoch() - peerprofiles.UPDATE_DELAY
            s += 1
            p.addScore(1)
            self.assertEqual(p.score, keydb.transportinfo.get_address_info(p.address, 'success'))

    def test_inc_score_with_sync_delay(self):
        p = peerprofiles.PeerProfiles(test_peers.pop())
        s = 0
        for x in range(2):
            s += 1
            p.addScore(1)
            if x == 0:
                self.assertEqual(p.score, keydb.transportinfo.get_address_info(p.address, 'success'))
            else:
                self.assertNotEqual(p.score, keydb.transportinfo.get_address_info(p.address, 'success'))

unittest.main()
