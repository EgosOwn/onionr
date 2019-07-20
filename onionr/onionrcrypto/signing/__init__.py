import base64, binascii
import nacl.encoding, nacl.signing, nacl.exceptions
import logger
def ed_sign(data, key, encodeResult=False):
    '''Ed25519 sign data'''
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
    try:
        key = nacl.signing.VerifyKey(key=key, encoder=nacl.encoding.Base32Encoder)
    except nacl.exceptions.ValueError:
        #logger.debug('Signature by unknown key (cannot reverse hash)')
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
    if encodedData:
        try:
            retData = key.verify(data, sig) # .encode() is not the same as nacl.encoding
        except nacl.exceptions.BadSignatureError:
            pass
    else:
        try:
            retData = key.verify(data, sig)
        except nacl.exceptions.BadSignatureError:
            pass
    return retData