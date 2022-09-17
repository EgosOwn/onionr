import traceback
import logger

from nacl.signing import VerifyKey

from wot.getbykey import get_identity_by_key
from wot.blockprocessingevent import WotCommand


def process_trust_signature(sig_payload: bytes):
    if len(sig_payload) != 129:
        logger.warn(
            f'Signature size is invalid for a signed identity')

    # verify that this is a signature for a trust command
    if sig_payload[0] != WotCommand.TRUST:
        logger.warn(
            f'Invalid command in signature')
        return
    # signer is first 32 bytes
    signer = VerifyKey(sig_payload[1:33])
    # signed is next 32 bytes
    signed = sig_payload[33:65]
    # signature is last 64 bytes
    signature = sig_payload[65:]

    # If bad signature, it raises nacl.exceptions.BadSignatureError
    signer.verify(int.to_bytes(sig_payload[0], 1, 'big') + signed, signature)

    # if good signature
    try:
        signer_identity = get_identity_by_key(signer)
        signed_identity = get_identity_by_key(signed)
    except KeyError:
        # if signer or signed identity are not in the identity set
        # this means they have not been announced yet
        traceback.print_exc()
        pass
    else:
        # noop if already signed
        signer_identity.trusted.add(signed_identity)
