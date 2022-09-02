# The web of trust is a graph of identities where each edge is a signature
# of a byte representing a trust level and an identity's public key
from typing import TYPE_CHECKING, Set

from .identity import Identity
from .blockprocessing import process_block


# Set of identites within N-distance trust
identities: Set['Identity'] = set()

