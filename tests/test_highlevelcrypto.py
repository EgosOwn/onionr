#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid, hashlib, base64
import nacl.exceptions
import nacl.signing, nacl.hash, nacl.encoding
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
from utils import createdirs
createdirs.create_dirs()
from onionrutils import stringvalidators, mnemonickeys
import onionrcrypto as crypto, onionrexceptions

class OnionrCryptoTests(unittest.TestCase):

    def test_blake2b(self):
        self.assertEqual(crypto.hashers.blake2b_hash('test'), crypto.hashers.blake2b_hash(b'test'))
        self.assertEqual(crypto.hashers.blake2b_hash(b'test'), crypto.hashers.blake2b_hash(b'test'))

        self.assertNotEqual(crypto.hashers.blake2b_hash(''), crypto.hashers.blake2b_hash(b'test'))
        try:
            crypto.hashers.blake2b_hash(None)
        except nacl.exceptions.TypeError:
            pass
        else:
            self.assertTrue(False)

        self.assertEqual(nacl.hash.blake2b(b'test'), crypto.hashers.blake2b_hash(b'test'))

    def test_sha3256(self):
        hasher = hashlib.sha3_256()
        self.assertEqual(crypto.hashers.sha3_hash('test'), crypto.hashers.sha3_hash(b'test'))
        self.assertEqual(crypto.hashers.sha3_hash(b'test'), crypto.hashers.sha3_hash(b'test'))

        self.assertNotEqual(crypto.hashers.sha3_hash(''), crypto.hashers.sha3_hash(b'test'))
        try:
            crypto.hashers.sha3_hash(None)
        except TypeError:
            pass
        else:
            self.assertTrue(False)

        hasher.update(b'test')
        normal = hasher.hexdigest()
        self.assertEqual(crypto.hashers.sha3_hash(b'test'), normal)

    def valid_default_id(self):
        self.assertTrue(stringvalidators.validate_pub_key(crypto.pub_key))

    def test_human_readable_length(self):
        human = mnemonickeys.get_human_readable_ID()
        self.assertTrue(len(human.split('-')) == 16)

    def test_safe_compare(self):
        self.assertTrue(crypto.cryptoutils.safe_compare('test', 'test'))
        self.assertTrue(crypto.cryptoutils.safe_compare('test', b'test'))
        self.assertFalse(crypto.cryptoutils.safe_compare('test', 'test2'))
        try:
            crypto.cryptoutils.safe_compare('test', None)
        except TypeError:
            pass
        else:
            self.assertTrue(False)

    def test_asymmetric(self):
        keyPair = crypto.generate()
        keyPair2 = crypto.generate()
        message = "hello world"

        self.assertTrue(len(crypto.encryption.pub_key_encrypt(message, keyPair2[0], encodedData=True)) > 0)
        encrypted = crypto.encryption.pub_key_encrypt(message, keyPair2[0], encodedData=False)
        decrypted = crypto.encryption.pub_key_decrypt(encrypted, privkey=keyPair2[1], encodedData=False)

        self.assertTrue(decrypted.decode() == message)
        try:
            crypto.encryption.pub_key_encrypt(None, keyPair2[0])
        except TypeError:
            pass
        else:
            self.assertTrue(False)

        blankMessage = crypto.encryption.pub_key_encrypt('', keyPair2[0])
        self.assertTrue('' == crypto.encryption.pub_key_decrypt(blankMessage, privkey=keyPair2[1], encodedData=False).decode())
        # Try to encrypt arbitrary bytes
        crypto.encryption.pub_key_encrypt(os.urandom(32), keyPair2[0])

    def test_pub_from_priv(self):
        priv = nacl.signing.SigningKey.generate().encode(encoder=nacl.encoding.Base32Encoder)
        pub = crypto.cryptoutils.getpubfrompriv.get_pub_key_from_priv(priv)
        self.assertTrue(stringvalidators.validate_pub_key(pub))

    def test_deterministic(self):
        password = os.urandom(32)
        gen = crypto.generate_deterministic(password)
        self.assertTrue(stringvalidators.validate_pub_key(gen[0]))
        try:
            crypto.generate_deterministic('weakpassword')
        except onionrexceptions.PasswordStrengthError:
            pass
        else:
            self.assertFalse(True)
        try:
            crypto.generate_deterministic(None)
        except TypeError:
            pass
        else:
            self.assertFalse(True)

        gen = crypto.generate_deterministic('weakpassword', bypassCheck=True)

        password = base64.b64encode(os.urandom(32))
        gen1 = crypto.generate_deterministic(password)
        gen2 = crypto.generate_deterministic(password)
        self.assertFalse(gen == gen1)
        self.assertTrue(gen1 == gen2)
        self.assertTrue(stringvalidators.validate_pub_key(gen1[0]))

unittest.main()
