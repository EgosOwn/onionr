from onionrtypes import OnionAddressString
from typing import Iterable

from collections import OrderedDict

from .extracted25519 import extract_ed25519_from_onion_address


def identify_neighbors(
        address: OnionAddressString,
        peers: Iterable[OnionAddressString],
        closest_n: int) -> OnionAddressString:

    address = extract_ed25519_from_onion_address(address)
    address_int = int.from_bytes(address, "big")

    def _calc_closeness(y):
        return abs(address_int - int.from_bytes(extract_ed25519_from_onion_address(y), "big"))

    closeness_values = []
    end_result = []
    for peer in peers:
        closeness_values.append((peer, _calc_closeness(peer)))
    closeness_values.sort()
    for i, result in enumerate(closeness_values):
        if i > closest_n:
            break
        end_result.append(result[0])
    return end_result
