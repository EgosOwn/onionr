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
from wot import identity
from wot.identity.identityset import identities


class WotCommand(IntEnum):
    TRUST = 1
    REVOKE_TRUST = auto()
    ANNOUNCE = auto()
    REVOKE = auto()


class TestSignatureRevokeProcessing(unittest.TestCase):
    def test_revoke_trust(self):
        # reset identity set
        identities.clear()

        fake_pubkey = secrets.token_bytes(32)
        signing_key = SigningKey.generate()

        main_iden = identity.Identity(signing_key.verify_key, "test")

        identities.add(main_iden)
        identities.add(identity.Identity(fake_pubkey, "test2"))

        wot_cmd = int(WotCommand.REVOKE_TRUST).to_bytes(1, 'big')
        revoke_signature = signing_key.sign(wot_cmd + fake_pubkey)
        revoke_signature_payload = wot_cmd + bytes(signing_key.verify_key) + \
            fake_pubkey + revoke_signature.signature

        main_iden.trusted.add(
            identity.Identity(VerifyKey(fake_pubkey), "test2"))

        identity.process_revoke_signature(revoke_signature_payload)

        self.assertEqual(len(identities), 2)
        self.assertEqual(len(list(identities)[0].trusted), 0)
        for iden in identities:
            if iden.key == signing_key.verify_key:
                for i in iden.trusted:
                    if i.key == VerifyKey(fake_pubkey):
                        raise AssertionError("Signed identity found")
                break

unittest.main()
