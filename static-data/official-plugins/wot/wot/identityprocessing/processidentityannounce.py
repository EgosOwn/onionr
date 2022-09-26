import logger

from nacl.signing import VerifyKey

from wot.blockprocessingevent import WotCommand
from wot.identity import Identity
from wot.identity.identityset import identities

def process_identity_announce(identity_announce_payload):

    # verify that this is a signature for an announce command
    if identity_announce_payload[0] != WotCommand.ANNOUNCE:
        logger.warn(
            f'Invalid command in signature' , terminal=True)
        return
    iden = Identity.deserialize(identity_announce_payload[1:])
    identities.add(iden)