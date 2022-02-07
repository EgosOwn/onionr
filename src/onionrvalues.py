"""Onionr - Private P2P Communication.

This file defines values and requirements used by Onionr
"""
import platform
import os

import filepaths
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
DENIABLE_PEER_ADDRESS = "OVPCZLOXD6DC5JHX4EQ3PSOGAZ3T24F75HQLIUZSDSMYPEOXCPFA"
PASSWORD_LENGTH = 25
ONIONR_TAGLINE = 'Private P2P Communication - GPLv3 - https://Onionr.net'
ONIONR_VERSION = '8.0.2'
ONIONR_VERSION_CODENAME = 'Genesis'
ONIONR_VERSION_TUPLE = tuple(ONIONR_VERSION.split('.')) # (MAJOR, MINOR, VERSION)
API_VERSION = '2' # increments of 1; only change when something fundamental about how the API works changes. This way other nodes know how to communicate without learning too much information about you.
MIN_PY_VERSION = 7 # min version of 7 so we can take advantage of non-cyclic type hints
DEVELOPMENT_MODE = False
IS_QUBES = False
"""limit type length for a block (soft enforced, ignored if invalid but block still stored)."""
MAX_BLOCK_TYPE_LENGTH = 15
"""limit clock timestamp for new blocks to be skewed in the future in seconds,
2 minutes to allow plenty of time for slow block insertion and slight clock inaccuracies"""
MAX_BLOCK_CLOCK_SKEW = 120
"""Onionr user IDs are ed25519 keys, which are always 32 bytes in length"""
MAIN_PUBLIC_KEY_SIZE = 32
ORIG_RUN_DIR_ENV_VAR = 'ORIG_ONIONR_RUN_DIR'

DATABASE_LOCK_TIMEOUT = 60

# Block creation anonymization requirements
MIN_BLOCK_UPLOAD_PEER_PERCENT = 0.1

WSGI_SERVER_REQUEST_TIMEOUT_SECS = 120

MAX_NEW_PEER_QUEUE = 1000

BLOCK_EXPORT_FILE_EXT = '.onionr'

# Begin OnionrValues migrated values

"""30 days is plenty of time for someone to decide to renew a block"""
DEFAULT_EXPIRE = 2678400
# Metadata header section length limits, in bytes
BLOCK_METADATA_LENGTHS = {'meta': 1000, 'sig': 200, 'signer': 200, 'time': 10,
                          'n': 1000, 'c': 1000, 'encryptType': 4, 'expire': 14}

# Pool Eligibility Max Age
BLOCK_POOL_MAX_AGE = 300

"""Public key that signs MOTD messages shown in the web UI"""
MOTD_SIGN_KEY = "TRH763JURNY47QPBTTQ4LLPYCYQK6Q5YA33R6GANKZK5C5DKCIGQ"

"""Public key that signs update notifications."""
UPDATE_SIGN_KEY = "TRH763JURNY47QPBTTQ4LLPYCYQK6Q5YA33R6GANKZK5C5DKCIGQ"


if os.path.exists(filepaths.daemon_mark_file):
    SCRIPT_NAME = 'start-daemon.sh'
else:
    SCRIPT_NAME = 'onionr.sh'
if 'qubes' in platform.release().lower():
    IS_QUBES = True
