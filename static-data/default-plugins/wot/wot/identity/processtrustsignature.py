import logger

from nacl.signing import VerifyKey

from ..getbykey import get_identity_by_key


def process_trust_signature(sig_payload: bytes):
    if len(sig_payload) != 128:
        logger.warn(
            f'Signature size is invalid for a signed identity')

    # signer is first 32 bytes
    signer = VerifyKey(sig_payload[:32])
    # signed is next 32 bytes
    signed = sig_payload[32:64]
    # signature is last 64 bytes
    signature = sig_payload[64:]

    # If bad signature, it raises nacl.exceptions.BadSignatureError
    signer.verify(signed, signature)

    # if good signature
    try:
        signer_identity = get_identity_by_key(signer)
        signed_identity = get_identity_by_key(signed)
    except KeyError:
        # if signer or signed identity are not in the identity set
        # this means they have not been announced yet
        pass
    else:
        # noop if already signed
        signer_identity.trusted.add(signed_identity)
