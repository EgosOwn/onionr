'''
    Onionr - Private P2P Communication

    convert a base32 string (intended for ed25519 user ids) to pgp word list
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
import base64

import mnemonic
import unpaddedbase32

import onionrcrypto
from etc import onionrvalues

m = mnemonic.Mnemonic('english')

def get_human_readable_ID(pub=''):
    '''gets a human readable ID from a public key'''
    if pub == '':
        pub = onionrcrypto.pub_key
    
    if not len(pub) == onionrvalues.MAIN_PUBLIC_KEY_SIZE:
        pub = base64.b32decode(pub)
    
    return m.to_mnemonic(pub).replace(' ', '-')

def get_base32(words):
    '''converts mnemonic to base32'''
    return unpaddedbase32.b32encode(m.to_entropy(words.replace('-', ' ')))
