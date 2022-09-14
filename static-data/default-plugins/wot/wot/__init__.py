# The web of trust is a graph of identities where each edge is a signature
# of a byte representing a trust level and an identity's public key
from typing import TYPE_CHECKING, Set

from .identity import Identity
from .getbykey import get_identity_by_key
from .identityset import identities

