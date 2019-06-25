import base64
from etc import pgpwords
def get_human_readable_ID(core_inst, pub=''):
    '''gets a human readable ID from a public key'''
    if pub == '':
        pub = core_inst._crypto.pubKey
    pub = base64.b16encode(base64.b32decode(pub)).decode()
    return ' '.join(pgpwords.wordify(pub))
