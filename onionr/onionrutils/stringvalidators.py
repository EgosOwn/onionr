import base64, string
import unpaddedbase32, nacl.signing, nacl.encoding
def validate_hash(utils_inst, data, length=64):
    '''
        Validate if a string is a valid hash hex digest (does not compare, just checks length and charset)
    '''
    retVal = True
    if data == False or data == True:
        return False
    data = data.strip()
    if len(data) != length:
        retVal = False
    else:
        try:
            int(data, 16)
        except ValueError:
            retVal = False

    return retVal

def validate_pub_key(utils_inst, key):
    '''
        Validate if a string is a valid base32 encoded Ed25519 key
    '''
    if type(key) is type(None):
        return False
    # Accept keys that have no = padding
    key = unpaddedbase32.repad(utils_inst.strToBytes(key))

    retVal = False
    try:
        nacl.signing.SigningKey(seed=key, encoder=nacl.encoding.Base32Encoder)
    except nacl.exceptions.ValueError:
        pass
    except base64.binascii.Error as err:
        pass
    else:
        retVal = True
    return retVal

def validate_transport(id):
    try:
        idLength = len(id)
        retVal = True
        idNoDomain = ''
        peerType = ''
        # i2p b32 addresses are 60 characters long (including .b32.i2p)
        if idLength == 60:
            peerType = 'i2p'
            if not id.endswith('.b32.i2p'):
                retVal = False
            else:
                idNoDomain = id.split('.b32.i2p')[0]
        # Onion v2's are 22 (including .onion), v3's are 62 with .onion
        elif idLength == 22 or idLength == 62:
            peerType = 'onion'
            if not id.endswith('.onion'):
                retVal = False
            else:
                idNoDomain = id.split('.onion')[0]
        else:
            retVal = False
        if retVal:
            if peerType == 'i2p':
                try:
                    id.split('.b32.i2p')[2]
                except:
                    pass
                else:
                    retVal = False
            elif peerType == 'onion':
                try:
                    id.split('.onion')[2]
                except:
                    pass
                else:
                    retVal = False
            if not idNoDomain.isalnum():
                retVal = False

            # Validate address is valid base32 (when capitalized and minus extension); v2/v3 onions and .b32.i2p use base32
            for x in idNoDomain.upper():
                if x not in string.ascii_uppercase and x not in '234567':
                    retVal = False

        return retVal
    except Exception as e:
        return False

def is_integer_string(data):
    '''Check if a string is a valid base10 integer (also returns true if already an int)'''
    try:
        int(data)
    except (ValueError, TypeError) as e:
        return False
    else:
        return True
