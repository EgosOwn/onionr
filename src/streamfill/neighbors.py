from onionrtypes import OnionAddressString
from typing import Iterable
from .extracted25519 import extract_ed25519_from_onion_address


def identify_neighbors(
        address: OnionAddressString,
        peers: Iterable[OnionAddressString],
        closest_n: int) -> OnionAddressString:

    address = extract_ed25519_from_onion_address(address)
    address_int = int.from_bytes(address, "big")

    def _calc_closeness(y):
        return abs(address_int - int.from_bytes(y, "big"))


    peer_ed_keys = list(map(extract_ed25519_from_onion_address, peers))
    differences = list(map(_calc_closeness, peer_ed_keys))

    return sorted(differences)[:closest_n]

