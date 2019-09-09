'''
    Onionr - Private P2P Communication

    validate various string data types
'''
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import base64, string
import unpaddedbase32, nacl.signing, nacl.encoding
from onionrutils import bytesconverter
def validate_hash(data, length=64):
    '''
        Validate if a string is a valid hash hex digest (does not compare, just checks length and charset)

        Length is only invalid if its *more* than the specified
    '''
    retVal = True
    if data == False or data == True:
        return False
    data = data.strip()
    if len(data) > length:
        retVal = False
    else:
        try:
            int(data, 16)
        except ValueError:
            retVal = False

    return retVal

def validate_pub_key(key):
    '''
        Validate if a string is a valid base32 encoded Ed25519 key
    '''
    if type(key) is type(None):
        return False
    # Accept keys that have no = padding
    key = unpaddedbase32.repad(bytesconverter.str_to_bytes(key))

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
                except IndexError:
                    pass
                else:
                    retVal = False
            elif peerType == 'onion':
                try:
                    id.split('.onion')[2]
                except IndexError:
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
