"""Onionr - Private P2P Communication.

functions to generate ed25519 key pairs
"""
import nacl.signing
import nacl.encoding
import nacl.pwhash

import onionrexceptions
from onionrutils import bytesconverter
from etc import onionrvalues
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


def generate_pub_key():
    """Generate a Ed25519 public key pair.

    return tuple of base32encoded pubkey, privkey
    """
    private_key = nacl.signing.SigningKey.generate()
    public_key = private_key.verify_key.encode(
        encoder=nacl.encoding.Base32Encoder())
    return (public_key.decode(), private_key.encode(
        encoder=nacl.encoding.Base32Encoder()).decode())


def generate_deterministic(passphrase, bypassCheck=False):
    """Generate a Ed25519 public key pair from a phase.

    not intended for human-generated key
    """
    passStrength = onionrvalues.PASSWORD_LENGTH
    # Convert to bytes if not already
    passphrase = bytesconverter.str_to_bytes(passphrase)
    # Validate passphrase length
    if not bypassCheck:
        if len(passphrase) < passStrength:
            raise onionrexceptions.PasswordStrengthError(
                "Passphase must be at least %s characters" % (passStrength,))
    # KDF values
    kdf = nacl.pwhash.argon2id.kdf
    # Does not need to be secret, but must be 16 bytes
    salt = b"U81Q7llrQcdTP0Ux"
    ops = nacl.pwhash.argon2id.OPSLIMIT_SENSITIVE
    mem = nacl.pwhash.argon2id.MEMLIMIT_SENSITIVE

    # Generate seed for ed25519 key
    key = kdf(32, passphrase, salt, opslimit=ops, memlimit=mem)
    key = nacl.signing.SigningKey(key)
    return (
        key.verify_key.encode(nacl.encoding.Base32Encoder).decode(),
        key.encode(nacl.encoding.Base32Encoder).decode())
