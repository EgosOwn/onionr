import nacl.signing, nacl.encoding
def generate_pub_key():
    '''Generate a Ed25519 public key pair, return tuple of base32encoded pubkey, privkey'''
    private_key = nacl.signing.SigningKey.generate()
    public_key = private_key.verify_key.encode(encoder=nacl.encoding.Base32Encoder())
    return (public_key.decode(), private_key.encode(encoder=nacl.encoding.Base32Encoder()).decode())