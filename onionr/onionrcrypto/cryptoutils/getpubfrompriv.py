from nacl import signing, encoding

from onionrtypes import UserID, UserIDSecretKey

def get_pub_key_from_priv(priv_key: UserIDSecretKey, raw_encoding:bool=False)->UserID:
    return signing.SigningKey(priv_key, encoder=encoding.Base32Encoder).verify_key.encode(encoding.Base32Encoder)
