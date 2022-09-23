import os, uuid
from random import randint
from time import sleep
from enum import IntEnum, auto
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError
import nacl
import secrets
import onionrblocks


TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

import unittest
import sys
sys.path.append(".")
sys.path.append('static-data/default-plugins/wot/')
sys.path.append("src/")
from wot.identityprocessing import process_identity_revoke
from wot import identity
from wot.identity.identityset import identities


class WotCommand(IntEnum):
    TRUST = 1
    REVOKE_TRUST = auto()
    ANNOUNCE = auto()
    REVOKE = auto()


class TestRevokeIdentityPayload(unittest.TestCase):

    def test_revoke_identity_invalid(self):
        identities.clear()

        signing_key = SigningKey.generate()
        main_iden = identity.Identity(signing_key, "test")
        identities.add(main_iden)

        wot_cmd = int(WotCommand.REVOKE).to_bytes(1, 'big')

        signed =  signing_key.sign(wot_cmd + bytes(main_iden.key))
        revoke_payload = wot_cmd + bytes(signing_key.verify_key) + signed.signature

        self.assertRaises(nacl.exceptions.Inv process_identity_revoke(revoke_payload)

        self.assertEqual(len(identities), 1)

    def test_revoke_identity_payload(self):
        identities.clear()

        signing_key = SigningKey.generate()
        main_iden = identity.Identity(signing_key, "test")
        identities.add(main_iden)

        wot_cmd = int(WotCommand.REVOKE).to_bytes(1, 'big')

        signed =  signing_key.sign(wot_cmd + bytes(main_iden.key))
        revoke_payload = wot_cmd + bytes(signing_key.verify_key) + signed.signature

        process_identity_revoke(revoke_payload)

        self.assertEqual(len(identities), 0)


unittest.main()
