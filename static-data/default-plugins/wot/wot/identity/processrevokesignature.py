import traceback

from nacl.signing import VerifyKey

import logger

from wot.getbykey import get_identity_by_key
from wot.blockprocessingevent import WotCommand


def process_revoke_signature(revoke_signature_payload):
    if len(revoke_signature_payload) != 129:
        logger.warn(
            f'Signature size is invalid for revoking an identity',
            terminal=True)

    # verify that this is a signature for a trust command
    if revoke_signature_payload[0] != WotCommand.REVOKE_TRUST:
        logger.warn(
            f'Invalid command in signature' , terminal=True)
        return
    # signer is first 32 bytes
    signer = VerifyKey(revoke_signature_payload[1:33])
    # revoked is next 32 bytes
    revoked = revoke_signature_payload[33:65]
    # signature is last 64 bytes
    signature = revoke_signature_payload[65:]

    # If bad signature, it raises nacl.exceptions.BadSignatureError
    signer.verify(
        int.to_bytes(revoke_signature_payload[0], 1, 'big') + \
        revoked, signature)

    # if good signature
    try:

        signer_identity = get_identity_by_key(bytes(signer))
        # noop if already revoked
        signer_identity.trusted.remove(get_identity_by_key(revoked))
    except KeyError:
        # if signer or revoked identity are not in the identity set
        # this means they have not been announced yet
        traceback.print_exc()
        pass