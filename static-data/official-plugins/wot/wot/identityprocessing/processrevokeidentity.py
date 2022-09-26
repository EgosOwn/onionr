import logger

from nacl.signing import VerifyKey

from wot.blockprocessingevent import WotCommand
from wot.identity import Identity
from wot.identity.identityset import identities

def process_identity_revoke(revoke_payload: bytes):
    wot_cmd = revoke_payload[0].to_bytes(1, 'big')
    if revoke_payload[0] != WotCommand.REVOKE:
        logger.warn(
            f'Invalid command in signature', terminal=True)
        return
    revoked_identity = revoke_payload[1:33]
    signature = revoke_payload[33:]

    # raises nacl.exceptions.BadSignatureError if bad signature
    VerifyKey(revoked_identity).verify(wot_cmd + revoked_identity, signature)
    
    identities.remove(Identity(revoked_identity, "etc"))
