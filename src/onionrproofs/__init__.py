"""Onionr - Private P2P Communication.

Proof of work module
"""
import multiprocessing, time, math, threading, binascii, sys, json
import nacl.encoding, nacl.hash, nacl.utils

import config
import logger
from onionrblocks import onionrblockapi
from onionrutils import bytesconverter
from onionrcrypto import hashers

from .blocknoncestart import BLOCK_NONCE_START_INT
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
config.reload()


def getDifficultyForNewBlock(data):
    """
    Get difficulty for block. Accepts size in integer, Block instance, or str/bytes full block contents
    """
    if isinstance(data, onionrblockapi.Block):
        dataSizeInBytes = len(bytesconverter.str_to_bytes(data.getRaw()))
    else:
        dataSizeInBytes = len(bytesconverter.str_to_bytes(data))

    minDifficulty = config.get('general.minimum_send_pow', 4)
    totalDifficulty = max(minDifficulty, math.floor(dataSizeInBytes / 1000000.0))

    return totalDifficulty


def getHashDifficulty(h: str):
    """
        Return the amount of leading zeroes in a hex hash string (hexHash)
    """
    return len(h) - len(h.lstrip('0'))


def hashMeetsDifficulty(hexHash):
    """
        Return bool for a hash string to see if it meets pow difficulty defined in config
    """
    hashDifficulty = getHashDifficulty(hexHash)

    try:
        expected = int(config.get('general.minimum_block_pow'))
    except TypeError:
        raise ValueError('Missing general.minimum_block_pow config')

    return hashDifficulty >= expected

