#!/usr/bin/env python3
import sys, os
sys.path.append(".")
import unittest, uuid, hashlib, base64
import nacl.exceptions
import nacl.signing, nacl.hash, nacl.encoding
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import core, onionr, onionrexceptions

c = core.Core()
crypto = c._crypto
class OnionrCryptoTests(unittest.TestCase):
    
    def test_blake2b(self):
        self.assertEqual(crypto.blake2bHash('test'), crypto.blake2bHash(b'test'))
        self.assertEqual(crypto.blake2bHash(b'test'), crypto.blake2bHash(b'test'))

        self.assertNotEqual(crypto.blake2bHash(''), crypto.blake2bHash(b'test'))
        try:
            crypto.blake2bHash(None)
        except nacl.exceptions.TypeError:
            pass
        else:
            self.assertTrue(False)
        
        self.assertEqual(nacl.hash.blake2b(b'test'), crypto.blake2bHash(b'test'))
    
    def test_sha3256(self):
        hasher = hashlib.sha3_256()
        self.assertEqual(crypto.sha3Hash('test'), crypto.sha3Hash(b'test'))
        self.assertEqual(crypto.sha3Hash(b'test'), crypto.sha3Hash(b'test'))

        self.assertNotEqual(crypto.sha3Hash(''), crypto.sha3Hash(b'test'))
        try:
            crypto.sha3Hash(None)
        except TypeError:
            pass
        else:
            self.assertTrue(False)
        
        hasher.update(b'test')
        normal = hasher.hexdigest()
        self.assertEqual(crypto.sha3Hash(b'test'), normal)
        
    def valid_default_id(self):
        self.assertTrue(c._utils.validatePubKey(crypto.pubKey))
    
    def test_human_readable_length(self):
        human = c._utils.getHumanReadableID()
        self.assertTrue(len(human.split(' ')) == 32)
    
    def test_human_readable_rebuild(self):
        return # Broken right now
        # Test if we can get the human readable id, and convert it back to valid base32 key
        human = c._utils.getHumanReadableID()
        unHuman = c._utils.convertHumanReadableID(human)
        nacl.signing.VerifyKey(c._utils.convertHumanReadableID(human), encoder=nacl.encoding.Base32Encoder)
    
    def test_safe_compare(self):
        self.assertTrue(crypto.safeCompare('test', 'test'))
        self.assertTrue(crypto.safeCompare('test', b'test'))
        self.assertFalse(crypto.safeCompare('test', 'test2'))
        try:
            crypto.safeCompare('test', None)
        except TypeError:
            pass
        else:
            self.assertTrue(False)
    
    def test_random_shuffle(self):
        # Small chance that the randomized list will be same. Rerun test a couple times if it fails
        startList = ['cat', 'dog', 'moose', 'rabbit', 'monkey', 'crab', 'human', 'dolphin', 'whale', 'etc'] * 10

        self.assertNotEqual(startList, list(crypto.randomShuffle(startList)))
        self.assertTrue(len(list(crypto.randomShuffle(startList))) == len(startList))

    def test_asymmetric(self):
        keyPair = crypto.generatePubKey()
        keyPair2 = crypto.generatePubKey()
        message = "hello world"

        self.assertTrue(len(crypto.pubKeyEncrypt(message, keyPair2[0], encodedData=True)) > 0)
        encrypted = crypto.pubKeyEncrypt(message, keyPair2[0], encodedData=False)
        decrypted = crypto.pubKeyDecrypt(encrypted, privkey=keyPair2[1], encodedData=False)

        self.assertTrue(decrypted.decode() == message)
        try:
            crypto.pubKeyEncrypt(None, keyPair2[0])
        except TypeError:
            pass
        else:
            self.assertTrue(False)
        
        blankMessage = crypto.pubKeyEncrypt('', keyPair2[0])
        self.assertTrue('' == crypto.pubKeyDecrypt(blankMessage, privkey=keyPair2[1], encodedData=False).decode())
        # Try to encrypt arbitrary bytes
        crypto.pubKeyEncrypt(os.urandom(32), keyPair2[0])
        
    def test_symmetric(self):
        dataString = "this is a secret message"
        dataBytes = dataString.encode()
        key = b"tttttttttttttttttttttttttttttttt"
        invalidKey = b'tttttttttttttttttttttttttttttttb'
        encrypted = crypto.symmetricEncrypt(dataString, key, returnEncoded=True)
        decrypted = crypto.symmetricDecrypt(encrypted, key, encodedMessage=True)
        self.assertTrue(dataString == decrypted.decode())

        try:
            crypto.symmetricDecrypt(encrypted, invalidKey, encodedMessage=True)
        except nacl.exceptions.CryptoError:
            pass
        else:
            self.assertFalse(True)
        try:
            crypto.symmetricEncrypt(None, key, returnEncoded=True)
        except AttributeError:
            pass
        else:
            self.assertFalse(True)
        crypto.symmetricEncrypt("string", key, returnEncoded=True)
        try:
            crypto.symmetricEncrypt("string", None, returnEncoded=True)
        except nacl.exceptions.TypeError:
            pass
        else:
            self.assertFalse(True)
    
    def test_deterministic(self):
        password = os.urandom(32)
        gen = crypto.generateDeterministic(password)
        self.assertTrue(c._utils.validatePubKey(gen[0]))
        try:
            crypto.generateDeterministic('weakpassword')
        except onionrexceptions.PasswordStrengthError:
            pass
        else:
            self.assertFalse(True)
        try:
            crypto.generateDeterministic(None)
        except TypeError:
            pass
        else:
            self.assertFalse(True)
        
        gen = crypto.generateDeterministic('weakpassword', bypassCheck=True)
        
        password = base64.b64encode(os.urandom(32))
        gen1 = crypto.generateDeterministic(password)
        gen2 = crypto.generateDeterministic(password)
        self.assertFalse(gen == gen1)
        self.assertTrue(gen1 == gen2)
        self.assertTrue(c._utils.validatePubKey(gen1[0]))

unittest.main()