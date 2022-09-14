import os, uuid
from random import randint
from time import sleep
from nacl.signing import SigningKey
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
from wot import identity
from wot import identityset

class TrustSignatureProcessing(unittest.TestCase):
    def test_processing_trust_payloads(self):
        # reset identity set
        identityset.identities = set()

        fake_pubkey = secrets.token_bytes(32)
        signing_key = SigningKey.generate()

        identityset.identities.add(identity.Identity(bytes(signing_key.verify_key), "test"))
        identityset.identities.add(identity.Identity(fake_pubkey, "test2"))


        trust_signature = signing_key.sign(fake_pubkey)
        trust_signature_payload = bytes(signing_key.verify_key) + fake_pubkey + \
            trust_signature.signature
        identity.process_trust_signature(trust_signature_payload)



        for iden in identityset.identities:
            if iden.key == signing_key.verify_key:
                self.assertIn(fake_pubkey, iden.trusted)
                break



unittest.main()
