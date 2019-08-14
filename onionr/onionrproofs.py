'''
    Onionr - Private P2P Communication

    Proof of work module
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
import multiprocessing, nacl.encoding, nacl.hash, nacl.utils, time, math, threading, binascii, sys, json, sys
import config, logger, onionrblockapi, storagecounter
from onionrutils import bytesconverter
from onionrcrypto import hashers
config.reload()

def getDifficultyModifier():
    '''returns the difficulty modifier for block storage based 
    on a variety of factors, currently only disk use.
    '''
    percentUse = storagecounter.StorageCounter().getPercent()
    difficultyIncrease = math.floor(4 * percentUse) # difficulty increase is a step function

    return difficultyIncrease

def getDifficultyForNewBlock(data):
    '''
    Get difficulty for block. Accepts size in integer, Block instance, or str/bytes full block contents
    '''
    if isinstance(data, onionrblockapi.Block):
        dataSizeInBytes = len(bytesconverter.str_to_bytes(data.getRaw()))
    else:
        dataSizeInBytes = len(bytesconverter.str_to_bytes(data))

    minDifficulty = config.get('general.minimum_send_pow', 4)
    totalDifficulty = max(minDifficulty, math.floor(dataSizeInBytes / 1000000.0)) + getDifficultyModifier()

    return totalDifficulty

def getHashDifficulty(hexHash):
    '''
        Return the amount of leading zeroes in a hex hash string (hexHash)
    '''
    assert type(hexHash) is str
    return len(hexHash) - len(hexHash.lstrip('0'))

def hashMeetsDifficulty(hexHash):
    '''
        Return bool for a hash string to see if it meets pow difficulty defined in config
    '''
    hashDifficulty = getHashDifficulty(hexHash)

    try:
        expected = int(config.get('general.minimum_block_pow'))
    except TypeError:
        raise ValueError('Missing general.minimum_block_pow config')

    return hashDifficulty >= expected

class DataPOW:
    def __init__(self, data, minDifficulty = 0, threadCount = 1):
        self.data = data
        self.threadCount = threadCount
        self.difficulty = max(minDifficulty, getDifficultyForNewBlock(data))
        self.rounds = 0
        self.hashing = False
        self.foundHash = False

        try:
            self.data = self.data.encode()
        except AttributeError:
            pass
        
        self.data = nacl.hash.blake2b(self.data)

        logger.info('Computing POW (difficulty: %s)...' % self.difficulty)

        self.mainHash = '0' * 70
        self.puzzle = self.mainHash[0:min(self.difficulty, len(self.mainHash))]
        
        for i in range(max(1, threadCount)):
            t = threading.Thread(name = 'thread%s' % i, target = self.pow, args = (True,))
            t.start()

    def pow(self, reporting = False):
        startTime = math.floor(time.time())
        self.hashing = True
        self.reporting = reporting
        iFound = False # if current thread is the one that found the answer
        
        while self.hashing:
            rand = nacl.utils.random()
            token = nacl.hash.blake2b(rand + self.data).decode()
            self.rounds += 1
            #print(token)
            if self.puzzle == token[0:self.difficulty]:
                self.hashing = False
                iFound = True
                break
                
        if iFound:
            endTime = math.floor(time.time())
            if self.reporting:
                logger.debug('Found token after %s seconds: %s' % (endTime - startTime, token), timestamp=True)
                logger.debug('Round count: %s' % (self.rounds,))
            self.result = (token, rand)

    def shutdown(self):
        self.hashing = False
        self.puzzle = ''

    def changeDifficulty(self, newDiff):
        self.difficulty = newDiff

    def getResult(self):
        '''
            Returns the result then sets to false, useful to automatically clear the result
        '''
        
        try:
            retVal = self.result
        except AttributeError:
            retVal = False
            
        self.result = False
        return retVal

    def waitForResult(self):
        '''
            Returns the result only when it has been found, False if not running and not found
        '''
        result = False
        try:
            while True:
                result = self.getResult()
                if not self.hashing:
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
            logger.warn('Got keyboard interrupt while waiting for POW result, stopping')
        return result

class POW:
    def __init__(self, metadata, data, threadCount = 1, minDifficulty=0):
        self.foundHash = False
        self.difficulty = 0
        self.data = data
        self.metadata = metadata
        self.threadCount = threadCount
        self.hashing = False

        json_metadata = json.dumps(metadata).encode()

        try:
            self.data = self.data.encode()
        except AttributeError:
            pass
            
        if minDifficulty > 0:
            self.difficulty = minDifficulty
        else:
            # Calculate difficulty. Dumb for now, may use good algorithm in the future.
            self.difficulty = getDifficultyForNewBlock(bytes(json_metadata + b'\n' + self.data))
            
        logger.info('Computing POW (difficulty: %s)...' % (self.difficulty,))

        self.mainHash = '0' * 64
        self.puzzle = self.mainHash[0:min(self.difficulty, len(self.mainHash))]

        for i in range(max(1, threadCount)):
            t = threading.Thread(name = 'thread%s' % i, target = self.pow, args = (True,))
            t.start()

    def pow(self, reporting = False):
        startTime = math.floor(time.time())
        self.hashing = True
        self.reporting = reporting
        iFound = False # if current thread is the one that found the answer
        nonce = int(binascii.hexlify(nacl.utils.random(64)), 16)
        while self.hashing:
            #token = nacl.hash.blake2b(rand + self.data).decode()
            self.metadata['pow'] = nonce
            payload = json.dumps(self.metadata).encode() + b'\n' + self.data
            token = hashers.sha3_hash(payload)
            try:
                # on some versions, token is bytes
                token = token.decode()
            except AttributeError:
                pass
            if self.puzzle == token[0:self.difficulty]:
                self.hashing = False
                iFound = True
                self.result = payload
                break
            nonce += 1
                
        if iFound:
            endTime = math.floor(time.time())
            if self.reporting:
                logger.debug('Found token after %s seconds: %s' % (endTime - startTime, token), timestamp=True)

    def shutdown(self):
        self.hashing = False
        self.puzzle = ''

    def changeDifficulty(self, newDiff):
        self.difficulty = newDiff

    def getResult(self):
        '''
            Returns the result then sets to false, useful to automatically clear the result
        '''
        
        try:
            retVal = self.result
        except AttributeError:
            retVal = False
            
        self.result = False
        return retVal

    def waitForResult(self):
        '''
            Returns the result only when it has been found, False if not running and not found
        '''
        result = False
        try:
            while True:
                result = self.getResult()
                if not self.hashing:
                    break
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
            logger.warn('Got keyboard interrupt while waiting for POW result, stopping')
        return result