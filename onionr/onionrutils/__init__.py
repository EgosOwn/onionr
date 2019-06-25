'''
    Onionr - Private P2P Communication

    OnionrUtils offers various useful functions to Onionr. Relatively misc.
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
# Misc functions that do not fit in the main api, but are useful
import sys, os, sqlite3, binascii, time, base64, json, glob, shutil, math, re, urllib.parse, string
import requests
import nacl.signing, nacl.encoding
import unpaddedbase32
import onionrexceptions, config, logger
import onionrevents
import storagecounter
from etc import pgpwords, onionrvalues
from . import localcommand, blockmetadata, basicrequests, validatemetadata
from . import stringvalidators

config.reload()
class OnionrUtils:
    '''
        Various useful functions for validating things, etc functions, connectivity
    '''
    def __init__(self, coreInstance):
        #self.fingerprintFile = 'data/own-fingerprint.txt' #TODO Remove since probably not needed
        self._core = coreInstance # onionr core instance

        self.avoidDupe = [] # list used to prevent duplicate requests per peer for certain actions
        self.peerProcessing = {} # dict of current peer actions: peer, actionList
        self.storageCounter = storagecounter.StorageCounter(self._core) # used to keep track of how much data onionr is using on disk
        return

    def escapeAnsi(self, line):
        '''
            Remove ANSI escape codes from a string with regex

            taken or adapted from: https://stackoverflow.com/a/38662876 by user https://stackoverflow.com/users/802365/%c3%89douard-lopez
            cc-by-sa-3 license https://creativecommons.org/licenses/by-sa/3.0/
        '''
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)

    def validateHash(self, data, length=64):
        '''
            Validate if a string is a valid hash hex digest (does not compare, just checks length and charset)
        '''
        return stringvalidators.validate_hash(self, data, length)

    def getEpoch(self):
        '''returns epoch'''
        return math.floor(time.time())

    def doPostRequest(self, url, data={}, port=0, proxyType='tor'):
        '''
        Do a POST request through a local tor or i2p instance
        '''
        return basicrequests.do_post_request(self, url, data, port, proxyType)

    def doGetRequest(self, url, port=0, proxyType='tor', ignoreAPI=False, returnHeaders=False):
        '''
        Do a get request through a local tor or i2p instance
        '''
        return basicrequests.do_get_request(self, url, port, proxyType, ignoreAPI, returnHeaders)

def size(path='.'):
    '''
        Returns the size of a folder's contents in bytes
    '''
    total = 0
    if os.path.exists(path):
        if os.path.isfile(path):
            total = os.path.getsize(path)
        else:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += size(entry.path)
    return total

def humanSize(num, suffix='B'):
    '''
        Converts from bytes to a human readable format.
    '''
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def has_block(core_inst, hash):
    '''
        Check for new block in the list
    '''
    conn = sqlite3.connect(core_inst.blockDB)
    c = conn.cursor()
    if not stringvalidators.validate_hash(hash):
        raise Exception("Invalid hash")
    for result in c.execute("SELECT COUNT() FROM hashes WHERE hash = ?", (hash,)):
        if result[0] >= 1:
            conn.commit()
            conn.close()
            return True
        else:
            conn.commit()
            conn.close()
            return False