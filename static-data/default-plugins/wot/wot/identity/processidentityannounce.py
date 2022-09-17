import logger

from nacl.signing import VerifyKey

from wot.blockprocessingevent import WotCommand
from wot.identity.identityset import identities

def process_identity_announce(identity_announce_payload):
    if len(identity_announce_payload) != 97:
        logger.warn(
            f'Identity announce signature size is invalid',
            terminal=True)

    # verify that this is a signature for an announce command
    if identity_announce_payload[0] != WotCommand.ANNOUNCE:
        logger.warn(
            f'Invalid command in signature' , terminal=True)
        return
    # signer is first 32 bytes
    signer = identity_announce_payload[1:33]
    # signature is last 64 bytes
    signature = identity_announce_payload[33:]

    # If bad signature, it raises nacl.exceptions.BadSignatureError
    VerifyKey(signer).verify(identity_announce_payload[0] + signer, signature)

    # noop if already announced
    identities.add