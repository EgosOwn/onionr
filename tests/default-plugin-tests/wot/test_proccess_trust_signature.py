import os, uuid
from random import randint
from time import sleep
from nacl.signing import SigningKey, VerifyKey
import nacl
import secrets
from enum import IntEnum, auto
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
from identityset import identities


class WotCommand(IntEnum):
    TRUST = 1
    REVOKE_TRUST = auto()
    ANNOUNCE = auto()
    REVOKE = auto()


class TrustSignatureProcessing(unittest.TestCase):
    def test_processing_trust_payload_without_announced_identity(self):
        # reset identity set
        identities.clear()

        fake_pubkey = secrets.token_bytes(32)
        signing_key = SigningKey.generate()

        identities.add(identity.Identity(signing_key.verify_key, "test"))

        wot_cmd = int(WotCommand.TRUST).to_bytes(1, 'big')

        trust_signature = signing_key.sign(wot_cmd + fake_pubkey)
        trust_signature_payload = wot_cmd + \
            bytes(signing_key.verify_key) + fake_pubkey + \
            trust_signature.signature

        for iden in identities:
            if iden.key == signing_key.verify_key:
                for i in iden.trusted:
                    if i.key == VerifyKey(fake_pubkey):
                        raise AssertionError("Signed identity found")
                break
        else:
            raise AssertionError("Signing identity not found")

    def test_processing_invalid_trust_payloads(self):
        # reset identity set
        identities.clear()

        fake_pubkey = secrets.token_bytes(32)
        signing_key = SigningKey.generate()

        identities.add(identity.Identity(signing_key.verify_key, "test"))
        identities.add(identity.Identity(VerifyKey(fake_pubkey), "test2"))

        wot_cmd = int(WotCommand.TRUST).to_bytes(1, 'big')

        trust_signature = signing_key.sign(wot_cmd + fake_pubkey)

        trust_signature = bytearray(trust_signature.signature)
        trust_signature[34] = 0
        trust_signature = bytes(trust_signature)
        trust_signature_payload = wot_cmd + bytes(signing_key.verify_key) + fake_pubkey + \
            trust_signature

        self.assertRaises(
            nacl.exceptions.BadSignatureError, identity.process_trust_signature, trust_signature_payload)

        for iden in identities:
            if iden.key == signing_key.verify_key:
                for i in iden.trusted:
                    if i.key == VerifyKey(fake_pubkey):
                        raise AssertionError("Signed identity found")
                break
        else:
            raise AssertionError("Signing identity not found")

    def test_processing_trust_payloads(self):
        # reset identity set
        identities.clear()

        fake_pubkey = secrets.token_bytes(32)
        signing_key = SigningKey.generate()

        identities.add(identity.Identity(signing_key.verify_key, "test"))
        identities.add(identity.Identity(VerifyKey(fake_pubkey), "test2"))

        wot_cmd = int(WotCommand.TRUST).to_bytes(1, 'big')

        trust_signature = signing_key.sign(wot_cmd + fake_pubkey)
        trust_signature_payload = wot_cmd + bytes(signing_key.verify_key) + fake_pubkey + \
            trust_signature.signature

        identity.process_trust_signature(trust_signature_payload)

        for iden in identities:
            if iden.key == signing_key.verify_key:

                for i in iden.trusted:
                    if i.key == VerifyKey(fake_pubkey):
                        break
                else:
                    raise AssertionError("Signed identity not found")
                break
        else:
            raise AssertionError("Signing identity not found")


unittest.main()


"""

"""