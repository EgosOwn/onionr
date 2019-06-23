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
from onionrblockapi import Block
import onionrexceptions, config, logger
import onionrevents
import storagecounter
from etc import pgpwords, onionrvalues
from onionrusers import onionrusers 
from . import localcommand, blockmetadata, validatemetadata, basicrequests

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

    def getRoundedEpoch(self, roundS=60):
        '''
            Returns the epoch, rounded down to given seconds (Default 60)
        '''
        epoch = self.getEpoch()
        return epoch - (epoch % roundS)
    
    def getClientAPIServer(self):
        retData = ''
        try:
            with open(self._core.privateApiHostFile, 'r') as host:
                hostname = host.read()
        except FileNotFoundError:
            raise FileNotFoundError
        else:
            retData += '%s:%s' % (hostname, config.get('client.client.port'))
        return retData

    def localCommand(self, command, data='', silent = True, post=False, postData = {}, maxWait=20):
        '''
            Send a command to the local http API server, securely. Intended for local clients, DO NOT USE for remote peers.
        '''
        return localcommand.local_command(self, command, data, silent, post, postData, maxWait)

    def getHumanReadableID(self, pub=''):
        '''gets a human readable ID from a public key'''
        if pub == '':
            pub = self._core._crypto.pubKey
        pub = base64.b16encode(base64.b32decode(pub)).decode()
        return ' '.join(pgpwords.wordify(pub))
    
    def convertHumanReadableID(self, pub):
        '''Convert a human readable pubkey id to base32'''
        pub = pub.lower()
        return self.bytesToStr(base64.b32encode(binascii.unhexlify(pgpwords.hexify(pub.strip()))))

    def getBlockMetadataFromData(self, blockData):
        '''
            accepts block contents as string, returns a tuple of 
            metadata, meta (meta being internal metadata, which will be 
            returned as an encrypted base64 string if it is encrypted, dict if not).
        '''
        return blockmetadata.get_block_metadata_from_data(self, blockData)

    def processBlockMetadata(self, blockHash):
        '''
            Read metadata from a block and cache it to the block database
        '''
        return blockmetadata.process_block_metadata(self, blockHash)

    def escapeAnsi(self, line):
        '''
            Remove ANSI escape codes from a string with regex

            taken or adapted from: https://stackoverflow.com/a/38662876 by user https://stackoverflow.com/users/802365/%c3%89douard-lopez
            cc-by-sa-3 license https://creativecommons.org/licenses/by-sa/3.0/
        '''
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)

    def hasBlock(self, hash):
        '''
            Check for new block in the list
        '''
        conn = sqlite3.connect(self._core.blockDB)
        c = conn.cursor()
        if not self.validateHash(hash):
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

    def hasKey(self, key):
        '''
            Check for key in list of public keys
        '''
        return key in self._core.listPeers()

    def validateHash(self, data, length=64):
        '''
            Validate if a string is a valid hash hex digest (does not compare, just checks length and charset)
        '''
        retVal = True
        if data == False or data == True:
            return False
        data = data.strip()
        if len(data) != length:
            retVal = False
        else:
            try:
                int(data, 16)
            except ValueError:
                retVal = False

        return retVal

    def validateMetadata(self, metadata, blockData):
        '''Validate metadata meets onionr spec (does not validate proof value computation), take in either dictionary or json string'''
        return validatemetadata.validate_metadata(self, metadata, blockData)

    def validatePubKey(self, key):
        '''
            Validate if a string is a valid base32 encoded Ed25519 key
        '''
        if type(key) is type(None):
            return False
        # Accept keys that have no = padding
        key = unpaddedbase32.repad(self.strToBytes(key))

        retVal = False
        try:
            nacl.signing.SigningKey(seed=key, encoder=nacl.encoding.Base32Encoder)
        except nacl.exceptions.ValueError:
            pass
        except base64.binascii.Error as err:
            pass
        else:
            retVal = True
        return retVal

    @staticmethod
    def validateID(id):
        '''
            Validate if an address is a valid tor or i2p hidden service
        '''
        try:
            idLength = len(id)
            retVal = True
            idNoDomain = ''
            peerType = ''
            # i2p b32 addresses are 60 characters long (including .b32.i2p)
            if idLength == 60:
                peerType = 'i2p'
                if not id.endswith('.b32.i2p'):
                    retVal = False
                else:
                    idNoDomain = id.split('.b32.i2p')[0]
            # Onion v2's are 22 (including .onion), v3's are 62 with .onion
            elif idLength == 22 or idLength == 62:
                peerType = 'onion'
                if not id.endswith('.onion'):
                    retVal = False
                else:
                    idNoDomain = id.split('.onion')[0]
            else:
                retVal = False
            if retVal:
                if peerType == 'i2p':
                    try:
                        id.split('.b32.i2p')[2]
                    except:
                        pass
                    else:
                        retVal = False
                elif peerType == 'onion':
                    try:
                        id.split('.onion')[2]
                    except:
                        pass
                    else:
                        retVal = False
                if not idNoDomain.isalnum():
                    retVal = False

                # Validate address is valid base32 (when capitalized and minus extension); v2/v3 onions and .b32.i2p use base32
                for x in idNoDomain.upper():
                    if x not in string.ascii_uppercase and x not in '234567':
                        retVal = False

            return retVal
        except:
            return False

    @staticmethod
    def isIntegerString(data):
        '''Check if a string is a valid base10 integer (also returns true if already an int)'''
        try:
            int(data)
        except (ValueError, TypeError) as e:
            return False
        else:
            return True

    def isCommunicatorRunning(self, timeout = 5, interval = 0.1):
        try:
            runcheck_file = self._core.dataDir + '.runcheck'

            if not os.path.isfile(runcheck_file):
                open(runcheck_file, 'w+').close()

            # self._core.daemonQueueAdd('runCheck') # deprecated
            starttime = time.time()

            while True:
                time.sleep(interval)

                if not os.path.isfile(runcheck_file):
                    return True
                elif time.time() - starttime >= timeout:
                    return False
        except:
            return False

    def importNewBlocks(self, scanDir=''):
        '''
            This function is intended to scan for new blocks ON THE DISK and import them
        '''
        blockList = self._core.getBlockList()
        exist = False
        if scanDir == '':
            scanDir = self._core.blockDataLocation
        if not scanDir.endswith('/'):
            scanDir += '/'
        for block in glob.glob(scanDir + "*.dat"):
            if block.replace(scanDir, '').replace('.dat', '') not in blockList:
                exist = True
                logger.info('Found new block on dist %s' % block)
                with open(block, 'rb') as newBlock:
                    block = block.replace(scanDir, '').replace('.dat', '')
                    if self._core._crypto.sha3Hash(newBlock.read()) == block.replace('.dat', ''):
                        self._core.addToBlockDB(block.replace('.dat', ''), dataSaved=True)
                        logger.info('Imported block %s.' % block)
                        self._core._utils.processBlockMetadata(block)
                    else:
                        logger.warn('Failed to verify hash for %s' % block)
        if not exist:
            logger.info('No blocks found to import')

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

    @staticmethod
    def strToBytes(data):
        try:
            data = data.encode()
        except AttributeError:
            pass
        return data
    @staticmethod
    def bytesToStr(data):
        try:
            data = data.decode()
        except AttributeError:
            pass
        return data

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