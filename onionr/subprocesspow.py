#!/usr/bin/env python3
import subprocess, sys, os
import multiprocessing, threading, time, json, math, binascii
from multiprocessing import Pipe, Process
import core, onionrblockapi, config, onionrutils, logger, onionrproofs

class SubprocessPOW:
    def __init__(self, data, metadata, core_inst=None, subprocCount=None):
        if core_inst is None:
            core_inst = core.Core()
        if subprocCount is None:
            subprocCount = os.cpu_count()
        self.subprocCount = subprocCount
        self.result = ''
        self.shutdown = False
        self.core_inst = core_inst
        self.data = data
        self.metadata = metadata

        dataLen = len(data) + len(json.dumps(metadata))

        #if forceDifficulty > 0:
        #    self.difficulty = forceDifficulty
        #else:
            # Calculate difficulty. Dumb for now, may use good algorithm in the future.
        self.difficulty = onionrproofs.getDifficultyForNewBlock(dataLen)
            
        try:
            self.data = self.data.encode()
        except AttributeError:
            pass
        
        logger.info('Computing POW (difficulty: %s)...' % self.difficulty)

        self.mainHash = '0' * 64
        self.puzzle = self.mainHash[0:min(self.difficulty, len(self.mainHash))]
        self.shutdown = False
        self.payload = None

    def start(self):
        startTime = self.core_inst._utils.getEpoch()
        for x in range(self.subprocCount):
            threading.Thread(target=self._spawn_proc).start()
        while True:
            if self.payload is None:
                time.sleep(0.1)
            else:
                self.shutdown = True
                return self.payload
    
    def _spawn_proc(self):
        parent_conn, child_conn = Pipe()
        p = Process(target=self.do_pow, args=(child_conn,))
        p.start()
        p.join()
        payload = None
        try:
            while True:
                data = parent_conn.recv()
                if len(data) >= 1:
                    payload = data
                    break
        except KeyboardInterrupt:
            pass
        finally:
            parent_conn.send('shutdown')
            self.payload = payload

    def do_pow(self, pipe):
        nonce = int(binascii.hexlify(os.urandom(2)), 16)
        nonceStart = nonce
        data = self.data
        metadata = self.metadata
        puzzle = self.puzzle
        difficulty = self.difficulty
        mcore = core.Core()
        while True:
            metadata['powRandomToken'] = nonce
            payload = json.dumps(metadata).encode() + b'\n' + data
            token = mcore._crypto.sha3Hash(payload)
            try:
                # on some versions, token is bytes
                token = token.decode()
            except AttributeError:
                pass
            if pipe.poll() and pipe.recv() == 'shutdown':
                break
            if puzzle == token[0:difficulty]:
                pipe.send(payload)
                break
            nonce += 1
        