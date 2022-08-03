"""
Onionr - Private P2P Communication

validate various string data types
"""
import base64
import string
import unpaddedbase32, nacl.signing, nacl.encoding
from onionrutils import bytesconverter
"""
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
"""


def validate_pub_key(key):
    """Validate if a string is a valid base32 encoded Ed25519 key"""
    if type(key) is type(None):
        return False
    # Accept keys that have no = padding
    key = unpaddedbase32.repad(bytesconverter.str_to_bytes(key))

    retVal = False
    try:
        nacl.signing.SigningKey(seed=key, encoder=nacl.encoding.Base32Encoder)
    except nacl.exceptions.ValueError:
        pass
    except base64.binascii.Error as _:
        pass
    else:
        retVal = True
    return retVal
