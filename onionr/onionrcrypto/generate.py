import nacl.signing, nacl.encoding, nacl.pwhash
import onionrexceptions
from onionrutils import bytesconverter
from etc import onionrvalues
def generate_pub_key():
    '''Generate a Ed25519 public key pair, return tuple of base32encoded pubkey, privkey'''
    private_key = nacl.signing.SigningKey.generate()
    public_key = private_key.verify_key.encode(encoder=nacl.encoding.Base32Encoder())
    return (public_key.decode(), private_key.encode(encoder=nacl.encoding.Base32Encoder()).decode())

def generate_deterministic(passphrase, bypassCheck=False):
    '''Generate a Ed25519 public key pair from a password'''
    passStrength = onionrvalues.PASSWORD_LENGTH
    passphrase = bytesconverter.str_to_bytes(passphrase) # Convert to bytes if not already
    # Validate passphrase length
    if not bypassCheck:
        if len(passphrase) < passStrength:
            raise onionrexceptions.PasswordStrengthError("Passphase must be at least %s characters" % (passStrength,))
    # KDF values
    kdf = nacl.pwhash.argon2id.kdf
    salt = b"U81Q7llrQcdTP0Ux" # Does not need to be unique or secret, but must be 16 bytes
    ops = nacl.pwhash.argon2id.OPSLIMIT_SENSITIVE
    mem = nacl.pwhash.argon2id.MEMLIMIT_SENSITIVE

    key = kdf(32, passphrase, salt, opslimit=ops, memlimit=mem) # Generate seed for ed25519 key
    key = nacl.signing.SigningKey(key)
    return (key.verify_key.encode(nacl.encoding.Base32Encoder).decode(), key.encode(nacl.encoding.Base32Encoder).decode())