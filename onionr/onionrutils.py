'''
    Onionr - P2P Microblogging Platform & Social network

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
import getpass, sys, requests, os, socket, hashlib, logger, sqlite3, config, binascii, time, base64, json, glob, shutil, math, json, re, urllib.parse, string
import nacl.signing, nacl.encoding
from onionrblockapi import Block
import onionrexceptions
from onionr import API_VERSION
import onionrevents
import storagecounter
from etc import pgpwords, onionrvalues
from onionrusers import onionrusers 
if sys.version_info < (3, 6):
    try:
        import sha3
    except ModuleNotFoundError:
        logger.fatal('On Python 3 versions prior to 3.6.x, you need the sha3 module')
        sys.exit(1)

class OnionrUtils:
    '''
        Various useful functions for validating things, etc functions, connectivity
    '''
    def __init__(self, coreInstance):
        #self.fingerprintFile = 'data/own-fingerprint.txt' #TODO Remove since probably not needed
        self._core = coreInstance # onionr core instance

        self.timingToken = '' # for when we make local connections to our http api, to bypass timing attack defense mechanism
        self.avoidDupe = [] # list used to prevent duplicate requests per peer for certain actions
        self.peerProcessing = {} # dict of current peer actions: peer, actionList
        self.storageCounter = storagecounter.StorageCounter(self._core) # used to keep track of how much data onionr is using on disk
        config.reload() # onionr config
        return

    def getTimeBypassToken(self):
        '''
            Load our timingToken from disk for faster local HTTP API
        '''
        try:
            if os.path.exists(self._core.dataDir + 'time-bypass.txt'):
                with open(self._core.dataDir + 'time-bypass.txt', 'r') as bypass:
                    self.timingToken = bypass.read()
        except Exception as error:
            logger.error('Failed to fetch time bypass token.', error = error)

        return self.timingToken

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
        config.reload()
        self.getTimeBypassToken()
        # TODO: URL encode parameters, just as an extra measure. May not be needed, but should be added regardless.
        hostname = ''
        waited = 0
        while hostname == '':
            try:
                hostname = self.getClientAPIServer()
            except FileNotFoundError:
                time.sleep(1)
                waited += 1
                if waited == maxWait:
                    return False
        if data != '':
            data = '&data=' + urllib.parse.quote_plus(data)
        payload = 'http://%s/%s%s' % (hostname, command, data)
        try:
            if post:
                retData = requests.post(payload, data=postData, headers={'token': config.get('client.webpassword'), 'Connection':'close'}, timeout=(maxWait, maxWait)).text
            else:
                retData = requests.get(payload, headers={'token': config.get('client.webpassword'), 'Connection':'close'}, timeout=(maxWait, maxWait)).text
        except Exception as error:
            if not silent:
                logger.error('Failed to make local request (command: %s):%s' % (command, error))
            retData = False

        return retData

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
        meta = {}
        metadata = {}
        data = blockData
        try:
            blockData = blockData.encode()
        except AttributeError:
            pass

        try:
            metadata = json.loads(blockData[:blockData.find(b'\n')].decode())
        except json.decoder.JSONDecodeError:
            pass
        else:
            data = blockData[blockData.find(b'\n'):].decode()

            if not metadata['encryptType'] in ('asym', 'sym'):
                try:
                    meta = json.loads(metadata['meta'])
                except KeyError:
                    pass
            meta = metadata['meta']
        return (metadata, meta, data)

    def processBlockMetadata(self, blockHash):
        '''
            Read metadata from a block and cache it to the block database
        '''
        onionrevents.event('processblocks', data = {'block': myBlock, 'type': blockType, 'signer': signer, 'validSig': valid}, onionr = None)
        curTime = self.getRoundedEpoch(roundS=60)
        myBlock = Block(blockHash, self._core)
        if myBlock.isEncrypted:
            myBlock.decrypt()
        if (myBlock.isEncrypted and myBlock.decrypted) or (not myBlock.isEncrypted):
            blockType = myBlock.getMetadata('type') # we would use myBlock.getType() here, but it is bugged with encrypted blocks
            signer = self.bytesToStr(myBlock.signer)
            valid = myBlock.verifySig()
            if myBlock.getMetadata('newFSKey') is not None:
                onionrusers.OnionrUser(self._core, signer).addForwardKey(myBlock.getMetadata('newFSKey'))
                
            try:
                if len(blockType) <= 10:
                    self._core.updateBlockInfo(blockHash, 'dataType', blockType)
            except TypeError:
                logger.warn("Missing block information")
                pass
            # Set block expire time if specified
            try:
                expireTime = myBlock.getHeader('expire')
                assert len(str(int(expireTime))) < 20 # test that expire time is an integer of sane length (for epoch)
            except (AssertionError, ValueError, TypeError) as e:
                expireTime = onionrvalues.OnionrValues().default_expire + curTime
            finally:
                self._core.updateBlockInfo(blockHash, 'expire', expireTime)
            if not blockType is None:
                self._core.updateBlockInfo(blockHash, 'dataType', blockType)
        else:
            pass
            #logger.debug('Not processing metadata on encrypted block we cannot decrypt.')

    def escapeAnsi(self, line):
        '''
            Remove ANSI escape codes from a string with regex

            taken or adapted from: https://stackoverflow.com/a/38662876
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
        # TODO, make this check sane sizes
        retData = False
        maxClockDifference = 60

        # convert to dict if it is json string
        if type(metadata) is str:
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                pass

        # Validate metadata dict for invalid keys to sizes that are too large
        maxAge = config.get("general.max_block_age", onionrvalues.OnionrValues().default_expire)
        if type(metadata) is dict:
            for i in metadata:
                try:
                    self._core.requirements.blockMetadataLengths[i]
                except KeyError:
                    logger.warn('Block has invalid metadata key ' + i)
                    break
                else:
                    testData = metadata[i]
                    try:
                        testData = len(testData)
                    except (TypeError, AttributeError) as e:
                        testData = len(str(testData))
                    if self._core.requirements.blockMetadataLengths[i] < testData:
                        logger.warn('Block metadata key ' + i + ' exceeded maximum size')
                        break
                if i == 'time':
                    if not self.isIntegerString(metadata[i]):
                        logger.warn('Block metadata time stamp is not integer string or int')
                        break
                    isFuture = (metadata[i] - self.getEpoch())
                    if isFuture > maxClockDifference:
                        logger.warn('Block timestamp is skewed to the future over the max %s: %s' (maxClockDifference, isFuture))
                        break
                    if (self.getEpoch() - metadata[i]) > maxAge:
                        logger.warn('Block is outdated: %s' % (metadata[i],))
                        break
                elif i == 'expire':
                    try:
                        assert int(metadata[i]) > self.getEpoch()
                    except AssertionError:
                        logger.warn('Block is expired: %s less than %s' % (metadata[i], self.getEpoch()))
                        break
                elif i == 'encryptType':
                    try:
                        assert metadata[i] in ('asym', 'sym', '')
                    except AssertionError:
                        logger.warn('Invalid encryption mode')
                        break
            else:
                # if metadata loop gets no errors, it does not break, therefore metadata is valid
                # make sure we do not have another block with the same data content (prevent data duplication and replay attacks)
                nonce = self._core._utils.bytesToStr(self._core._crypto.sha3Hash(blockData))
                try:
                    with open(self._core.dataNonceFile, 'r') as nonceFile:
                        if nonce in nonceFile.read():
                            retData = False # we've seen that nonce before, so we can't pass metadata
                            raise onionrexceptions.DataExists
                except FileNotFoundError:
                    retData = True
                except onionrexceptions.DataExists:
                    # do not set retData to True, because nonce has been seen before
                    pass
                else:
                    retData = True
        else:
            logger.warn('In call to utils.validateMetadata, metadata must be JSON string or a dictionary object')

        return retData

    def validatePubKey(self, key):
        '''
            Validate if a string is a valid base32 encoded Ed25519 key
        '''
        retVal = False
        if type(key) is type(None):
            return False
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
            print('No blocks found to import')

    def progressBar(self, value = 0, endvalue = 100, width = None):
        '''
            Outputs a progress bar with a percentage. Write \n after use.
        '''

        if width is None or height is None:
            width, height = shutil.get_terminal_size((80, 24))

        bar_length = width - 6

        percent = float(value) / endvalue
        arrow = '─' * int(round(percent * bar_length)-1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        sys.stdout.write("\r┣{0}┫ {1}%".format(arrow + spaces, int(round(percent * 100))))
        sys.stdout.flush()

    def getEpoch(self):
        '''returns epoch'''
        return math.floor(time.time())

    def doPostRequest(self, url, data={}, port=0, proxyType='tor'):
        '''
        Do a POST request through a local tor or i2p instance
        '''
        if proxyType == 'tor':
            if port == 0:
                port = self._core.torPort
            proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
        elif proxyType == 'i2p':
            proxies = {'http': 'http://127.0.0.1:4444'}
        else:
            return
        headers = {'user-agent': 'PyOnionr', 'Connection':'close'}
        try:
            proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
            r = requests.post(url, data=data, headers=headers, proxies=proxies, allow_redirects=False, timeout=(15, 30))
            retData = r.text
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except requests.exceptions.RequestException as e:
            logger.debug('Error: %s' % str(e))
            retData = False
        return retData

    def doGetRequest(self, url, port=0, proxyType='tor', ignoreAPI=False, returnHeaders=False):
        '''
        Do a get request through a local tor or i2p instance
        '''
        retData = False
        if proxyType == 'tor':
            if port == 0:
                raise onionrexceptions.MissingPort('Socks port required for Tor HTTP get request')
            proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
        elif proxyType == 'i2p':
            proxies = {'http': 'http://127.0.0.1:4444'}
        else:
            return
        headers = {'user-agent': 'PyOnionr', 'Connection':'close'}
        response_headers = dict()
        try:
            proxies = {'http': 'socks4a://127.0.0.1:' + str(port), 'https': 'socks4a://127.0.0.1:' + str(port)}
            r = requests.get(url, headers=headers, proxies=proxies, allow_redirects=False, timeout=(15, 30), )
            # Check server is using same API version as us
            if not ignoreAPI:
                try:
                    response_headers = r.headers
                    if r.headers['X-API'] != str(API_VERSION):
                        raise onionrexceptions.InvalidAPIVersion
                except KeyError:
                    raise onionrexceptions.InvalidAPIVersion
            retData = r.text
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except ValueError as e:
            logger.debug('Failed to make GET request to %s' % url, error = e, sensitive = True)
        except onionrexceptions.InvalidAPIVersion:
            if 'X-API' in response_headers:
                logger.debug('Using API version %s. Cannot communicate with node\'s API version of %s.' % (API_VERSION, response_headers['X-API']))
            else:
                logger.debug('Using API version %s. API version was not sent with the request.' % API_VERSION)
        except requests.exceptions.RequestException as e:
            if not 'ConnectTimeoutError' in str(e) and not 'Request rejected or failed' in str(e):
                logger.debug('Error: %s' % str(e))
            retData = False
        if returnHeaders:
            return (retData, response_headers)
        else:
            return retData

    def strToBytes(self, data):
        try:
            data = data.encode()
        except AttributeError:
            pass
        return data
    def bytesToStr(self, data):
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