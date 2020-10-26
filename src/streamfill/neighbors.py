from onionrtypes import OnionAddressString
from typing import Iterable

from collections import OrderedDict

from .extracted25519 import extract_ed25519_from_onion_address


def identify_neighbors(
        address: OnionAddressString,
        peers: Iterable[OnionAddressString],
        closest_n: int) -> OnionAddressString:
    """Identify node addresses that are closest
    in value to a given node address"""
    peers_to_test = list(peers)

    try:
        peers_to_test.remove(address)
    except ValueError:
        pass

    address = extract_ed25519_from_onion_address(address)
    address_int = int.from_bytes(address, "big")
    closeness_values = []
    end_result = []

    def _calc_closeness(y):
        ret = abs(
            address_int -
            int.from_bytes(extract_ed25519_from_onion_address(y), "big"))
        return ret

    for peer in peers_to_test:
        closeness_values.append((peer, _calc_closeness(peer)))
    closeness_values.sort(key=lambda p: p[1])
    for i, result in enumerate(closeness_values):
        end_result.append(result[0])
        if i > closest_n:
            break
    return end_result
