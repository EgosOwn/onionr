from enum import Enum

from .phase import DandelionPhase

class StemAcceptResult:
    DENY = int(0).to_bytes(1, 'big')
    ALLOW = int(1).to_bytes(1, 'big')
