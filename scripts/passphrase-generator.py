#!/usr/bin/env python3

"""Generate a 16 word passphase with 256 bits of entropy.

Specify true to reduce to 128 bits"""


import sys

import niceware

byte_count = 32  # 256 bits of entropy with niceware

arg = False
try:
    arg = sys.argv[1].lower()
    if arg == 'true':
        byte_count = 16
except IndexError: pass

print(' '.join(niceware.generate_passphrase(byte_count)))
