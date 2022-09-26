import os, uuid
from random import randint
from time import sleep
from enum import IntEnum, auto
from nacl.signing import SigningKey, VerifyKey
import nacl
import secrets
import onionrblocks


TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

import unittest
import sys
sys.path.append(".")
sys.path.append('static-data/official-plugins/wot/')
sys.path.append("src/")
from wot.identityprocessing import process_identity_announce
from wot import identity
from wot.identity.identityset import identities


class WotCommand(IntEnum):
    TRUST = 1
    REVOKE_TRUST = auto()
    ANNOUNCE = auto()
    REVOKE = auto()


class TestAnnounceIdentityPayload(unittest.TestCase):
    def test_announce_identity_payload(self):
        # reset identity set
        identities.clear()

        signing_key = SigningKey.generate()
        main_iden = identity.Identity(signing_key, "test")

        wot_cmd = int(WotCommand.ANNOUNCE).to_bytes(1, 'big')
        serialized_iden = wot_cmd + main_iden.serialize()

        process_identity_announce(serialized_iden)

        self.assertEqual(bytes(main_iden.key), bytes(list(identities)[0].key))
        self.assertEqual(len(identities), 1)
        self.assertEqual(len(main_iden.trusted), 0)



unittest.main()
