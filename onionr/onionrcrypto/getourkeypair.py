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
