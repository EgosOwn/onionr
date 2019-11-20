"""
    Onionr - Private P2P Communication

    returns our current active keypair
"""
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
import os
import keymanager, config, filepaths
from . import generate
def get_keypair():
    key_m = keymanager.KeyManager()
    if os.path.exists(filepaths.keys_file):
        if len(config.get('general.public_key', '')) > 0:
            pubKey = config.get('general.public_key')
        else:
            pubKey = key_m.getPubkeyList()[0]
        privKey = key_m.getPrivkey(pubKey)
    else:
        keys = generate.generate_pub_key()
        pubKey = keys[0]
        privKey = keys[1]
        key_m.addKey(pubKey, privKey)
    return (pubKey, privKey)
