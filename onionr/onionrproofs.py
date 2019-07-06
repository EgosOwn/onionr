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
import multiprocessing, nacl.encoding, nacl.hash, nacl.utils, time, math, threading, binascii, sys, json
import core, config, logger, onionrblockapi
from onionrutils import bytesconverter

config.reload()

def getDifficultyModifier(coreOrUtilsInst=None):
    '''Accepts a core or utils instance returns
    the difficulty modifier for block storage based
    on a variety of factors, currently only disk use.
    '''
    classInst = coreOrUtilsInst
    retData = 0
    useFunc = classInst.storage_counter.getPercent

    percentUse = useFunc()

    if percentUse >= 0.50:
        retData += 1
    elif percentUse >= 0.75:
        retData += 2
    elif percentUse >= 0.95:
        retData += 3

    return retData

def getDifficultyForNewBlock(data, ourBlock=True, coreInst=None):
    '''
    Get difficulty for block. Accepts size in integer, Block instance, or str/bytes full block contents
    '''
    retData = 0
    dataSize = 0
    if isinstance(data, onionrblockapi.Block):
        dataSize = len(data.getRaw().encode('utf-8'))
    else:
        dataSize = len(bytesconverter.str_to_bytes(data))

    if ourBlock:
        minDifficulty = config.get('general.minimum_send_pow', 4)
    else:
        minDifficulty = config.get('general.minimum_block_pow', 4)

    retData = max(minDifficulty, math.floor(dataSize / 100000)) + getDifficultyModifier(coreInst)

    return retData

def getHashDifficulty(h):
    '''
        Return the amount of leading zeroes in a hex hash string (h)
    '''
    difficulty = 0
    assert type(h) is str
    for character in h:
        if character == '0':
            difficulty += 1
        else:
            break
    return difficulty

def hashMeetsDifficulty(h):
    '''
        Return bool for a hash string to see if it meets pow difficulty defined in config
    '''
    hashDifficulty = getHashDifficulty(h)
    try:
        expected = int(config.get('general.minimum_block_pow'))
    except TypeError:
        raise ValueError('Missing general.minimum_block_pow config')
    if hashDifficulty >= expected:
        return True
    else:
        return False

class DataPOW:
    def __init__(self, data, forceDifficulty=0, threadCount = 1):
        self.foundHash = False
        self.difficulty = 0
        self.data = data
        self.threadCount = threadCount
        self.rounds = 0

        if forceDifficulty == 0:
            dataLen = sys.getsizeof(data)
            self.difficulty = math.floor(dataLen / 1000000)
            if self.difficulty <= 2:
                self.difficulty = 4
        else:
            self.difficulty = forceDifficulty

        try:
            self.data = self.data.encode()
        except AttributeError:
            pass

        self.data = nacl.hash.blake2b(self.data)

        logger.debug('Computing POW (difficulty: %s)...' % self.difficulty)

        self.mainHash = '0' * 70
        self.puzzle = self.mainHash[0:min(self.difficulty, len(self.mainHash))]

        myCore = core.Core()
        for i in range(max(1, threadCount)):
            t = threading.Thread(name = 'thread%s' % i, target = self.pow, args = (True,myCore))
            t.start()

    def pow(self, reporting = False, myCore = None):
        startTime = math.floor(time.time())
        self.hashing = True
        self.reporting = reporting
        iFound = False # if current thread is the one that found the answer
        answer = ''
        heartbeat = 200000
        hbCount = 0

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
    def __init__(self, metadata, data, threadCount = 1, forceDifficulty=0, coreInst=None):
        self.foundHash = False
        self.difficulty = 0
        self.data = data
        self.metadata = metadata
        self.threadCount = threadCount

        try:
            assert isinstance(coreInst, core.Core)
        except AssertionError:
            myCore = core.Core()
        else:
            myCore = coreInst

        json_metadata = json.dumps(metadata).encode()

        try:
            self.data = self.data.encode()
        except AttributeError:
            pass

        if forceDifficulty > 0:
            self.difficulty = forceDifficulty
        else:
            # Calculate difficulty. Dumb for now, may use good algorithm in the future.
            self.difficulty = getDifficultyForNewBlock(bytes(json_metadata + b'\n' + self.data), coreInst=myCore)


        logger.debug('Computing POW (difficulty: %s)...' % self.difficulty)

        self.mainHash = '0' * 64
        self.puzzle = self.mainHash[0:min(self.difficulty, len(self.mainHash))]

        for i in range(max(1, threadCount)):
            t = threading.Thread(name = 'thread%s' % i, target = self.pow, args = (True,myCore))
            t.start()
        self.myCore = myCore
        return

    def pow(self, reporting = False, myCore = None):
        startTime = math.floor(time.time())
        self.hashing = True
        self.reporting = reporting
        iFound = False # if current thread is the one that found the answer
        answer = ''
        hbCount = 0
        nonce = int(binascii.hexlify(nacl.utils.random(2)), 16)
        startNonce = nonce
        while self.hashing:
            #token = nacl.hash.blake2b(rand + self.data).decode()
            self.metadata['pow'] = nonce
            payload = json.dumps(self.metadata).encode() + b'\n' + self.data
            token = myCore._crypto.sha3Hash(payload)
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
