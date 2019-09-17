'''
    Onionr - Private P2P Communication

    This file defines values and requirements used by Onionr
'''
'''
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
'''
import platform
DENIABLE_PEER_ADDRESS = "OVPCZLOXD6DC5JHX4EQ3PSOGAZ3T24F75HQLIUZSDSMYPEOXCPFA===="
PASSWORD_LENGTH = 25
ONIONR_TAGLINE = 'Private P2P Communication - GPLv3 - https://Onionr.net'
ONIONR_VERSION = '0.0.0' # for debugging and stuff
ONIONR_VERSION_TUPLE = tuple(ONIONR_VERSION.split('.')) # (MAJOR, MINOR, VERSION)
API_VERSION = '0' # increments of 1; only change when something fundamental about how the API works changes. This way other nodes know how to communicate without learning too much information about you.
MIN_PY_VERSION = 7
DEVELOPMENT_MODE = True
MAX_BLOCK_TYPE_LENGTH = 15
MAX_BLOCK_CLOCK_SKEW = 120
MAIN_PUBLIC_KEY_SIZE = 32
ORIG_RUN_DIR_ENV_VAR = 'ORIG_ONIONR_RUN_DIR'

# Block creation anonymization requirements
MIN_BLOCK_UPLOAD_PEER_PERCENT = 0.1

# Begin OnionrValues migrated values
ANNOUNCE_POW = 5
DEFAULT_EXPIRE = 2592000
BLOCK_METADATA_LENGTHS = {'meta': 1000, 'sig': 200, 'signer': 200, 'time': 10, 'pow': 1000, 'encryptType': 4, 'expire': 14}

platform = platform.system()
if platform == 'Windows':
    SCRIPT_NAME = 'run-windows.bat'
else:
    SCRIPT_NAME = 'onionr.sh'
