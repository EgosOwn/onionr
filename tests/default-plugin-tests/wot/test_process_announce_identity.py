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
sys.path.append('static-data/default-plugins/wot/wot')
sys.path.append("src/")
import identity
from identity.identityset import identities


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
        main_iden = identity.Identity(signing_key.verify_key, "test")

        wot_cmd = int(WotCommand.ANNOUNCE).to_bytes(1, 'big')
        announce_signature = signing_key.sign(wot_cmd + bytes(main_iden))
        announce_signature_payload = wot_cmd + bytes(signing_key.verify_key) + \
            bytes(announce_signature)

        identity.process_identity_announce(announce_signature_payload)

        self.assertEqual(main_iden, identities[0])
        self.assertEqual(len(identities), 1)
        self.assertEqual(len(main_iden.trusted), 0)



unittest.main()
