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
from etc import pgpwords
def get_human_readable_ID(core_inst, pub=''):
    '''gets a human readable ID from a public key'''
    if pub == '':
        pub = core_inst._crypto.pubKey
    pub = base64.b16encode(base64.b32decode(pub)).decode()
    return ' '.join(pgpwords.wordify(pub))
