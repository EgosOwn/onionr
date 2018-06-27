'''
    Onionr - P2P Microblogging Platform & Social network

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

import nacl.encoding, nacl.hash, nacl.utils, time, math, threading, binascii, logger, sys, base64
import core

class POW:
    def __init__(self, data, threadCount = 5):
        self.foundHash = False
        self.difficulty = 0
        self.data = data
        self.threadCount = threadCount

        dataLen = sys.getsizeof(data)
        self.difficulty = math.floor(dataLen / 1000000)
        if self.difficulty <= 2:
            self.difficulty = 4

        try:
            self.data = self.data.encode()
        except AttributeError:
            pass
        
        self.data = nacl.hash.blake2b(self.data)

        logger.info('Computing POW (difficulty: %s)...' % self.difficulty)

        self.mainHash = '0' * 70
        self.puzzle = self.mainHash[0:min(self.difficulty, len(self.mainHash))]
        
        myCore = core.Core()
        for i in range(max(1, threadCount)):
            t = threading.Thread(name = 'thread%s' % i, target = self.pow, args = (True,myCore))
            t.start()
        
        return

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
            #print(token)
            if self.puzzle == token[0:self.difficulty]:
                self.hashing = False
                iFound = True
                break
                
        if iFound:
            endTime = math.floor(time.time())
            if self.reporting:
                logger.debug('Found token after %s seconds: %s' % (endTime - startTime, token), timestamp=True)
                logger.debug('Random value was: %s' % base64.b64encode(rand).decode())
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
                    time.sleep(2)
        except KeyboardInterrupt:
            self.shutdown()
            logger.warn('Got keyboard interrupt while waiting for POW result, stopping')
        return result