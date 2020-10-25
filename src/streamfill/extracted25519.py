from base64 import b32decode
from typing import TYPE_CHECKING

from onionrutils.bytesconverter import str_to_bytes

if TYPE_CHECKING:
    from onionrtypes import Ed25519PublicKeyBytes, OnionAddressString


def extract_ed25519_from_onion_address(
        address: 'OnionAddressString') -> 'Ed25519PublicKeyBytes':
    address = str_to_bytes(address).replace(b'.onion', b'').upper()
    ed25519 = b32decode(address)[:-3]
    return ed25519