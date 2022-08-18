from collections import deque
from typing import Set, Union, List


identities: List['Identity'] = []


class Identity:
    def __init__(self, key: Union['Ed25519PublicKey', 'Ed25519PrivateKey']):
        self.trusted: Set[Identity] = set()
        self.key = key

    def __eq__(self, other):
        return self.key == other

    def __str__(self):
        return self.key

    def __hash__(self):
        return hash(self.key)


def get_distance(identity: Identity, identity2: Identity):
    distance = 0
    visited = set()
    stack = deque([identity])

    while stack:
        current_iden = stack.popleft()

        if current_iden == identity2:
            return distance
        distance += 1

        if identity2 in current_iden.trusted:
            return distance

        for trusted in current_iden.trusted:
            if trusted not in visited:
                visited.add(trusted)
                stack.append(trusted)
    raise ValueError
