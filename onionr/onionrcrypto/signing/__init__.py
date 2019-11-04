import base64, binascii

import unpaddedbase32
import nacl.encoding, nacl.signing, nacl.exceptions

from onionrutils import bytesconverter
from onionrutils import mnemonickeys
import logger

def ed_sign(data, key, encodeResult=False):
    '''Ed25519 sign data'''
    key = unpaddedbase32.repad(bytesconverter.str_to_bytes(key))
    try:
        data = data.encode()
    except AttributeError:
        pass
    key = nacl.signing.SigningKey(seed=key, encoder=nacl.encoding.Base32Encoder)
    retData = ''
    if encodeResult:
        retData = key.sign(data, encoder=nacl.encoding.Base64Encoder).signature.decode() # .encode() is not the same as nacl.encoding
    else:
        retData = key.sign(data).signature
    return retData

def ed_verify(data, key, sig, encodedData=True):
    '''Verify signed data (combined in nacl) to an ed25519 key'''
    key = unpaddedbase32.repad(bytesconverter.str_to_bytes(key))
    try:
        key = nacl.signing.VerifyKey(key=key, encoder=nacl.encoding.Base32Encoder)
    except nacl.exceptions.ValueError:
        return False
    except binascii.Error:
        logger.warn('Could not load key for verification, invalid padding')
        return False
    retData = False
    sig = base64.b64decode(sig)
    try:
        data = data.encode()
    except AttributeError:
        pass
    try:
        retData = key.verify(data, sig) # .encode() is not the same as nacl.encoding
    except nacl.exceptions.BadSignatureError:
        pass
    return retData
