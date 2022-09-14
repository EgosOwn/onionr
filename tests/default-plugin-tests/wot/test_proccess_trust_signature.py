import os, uuid
from random import randint
from time import sleep
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
from identityset import identities


class TrustSignatureProcessing(unittest.TestCase):

    def test_processing_trust_payload_without_announced_identity(self):
        # reset identity set
        identities.clear()

        fake_pubkey = secrets.token_bytes(32)
        signing_key = SigningKey.generate()

        identities.add(identity.Identity(signing_key.verify_key, "test"))

        trust_signature = signing_key.sign(fake_pubkey)
        trust_signature_payload = bytes(signing_key.verify_key) + fake_pubkey + \
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

        trust_signature = signing_key.sign(fake_pubkey)
        trust_signature_payload = bytes(signing_key.verify_key) + fake_pubkey + \
            trust_signature.signature
        trust_signature_payload = bytearray(trust_signature_payload)
        trust_signature_payload[64] = 0
        trust_signature_payload = bytes(trust_signature_payload)


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


        trust_signature = signing_key.sign(fake_pubkey)
        trust_signature_payload = bytes(signing_key.verify_key) + fake_pubkey + \
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