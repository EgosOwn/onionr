#!/usr/bin/env python3
import subprocess, os
import multiprocessing, threading, time, json
from multiprocessing import Pipe, Process
import core, onionrblockapi, config, onionrutils, logger, onionrproofs

class SubprocessPOW:
    def __init__(self, data, metadata, core_inst=None, subproc_count=None):
        '''
            Onionr proof of work using multiple processes
            Accepts block data, block metadata 
            and optionally an onionr core library instance.
            if subproc_count is not set, os.cpu_count() is used to determine the number of processes

            Do to Python GIL multiprocessing or use of external libraries is necessary to accelerate CPU bound tasks
        '''
        # Option to accept existing core instance to save memory
        if core_inst is None:
            core_inst = core.Core()
        # No known benefit to using more processes than there are cores.
        # Note: os.cpu_count perhaps not always accurate
        if subproc_count is None:
            subproc_count = os.cpu_count()
        self.subproc_count = subproc_count
        self.result = ''
        self.shutdown = False
        self.core_inst = core_inst
        self.data = data
        self.metadata = metadata

        # dump dict to measure bytes of json metadata. Cannot reuse later because the pow token must be added
        json_metadata = json.dumps(metadata).encode()

        self.data = onionrutils.OnionrUtils.strToBytes(data)
        # Calculate difficulty. Dumb for now, may use good algorithm in the future.
        self.difficulty = onionrproofs.getDifficultyForNewBlock(bytes(json_metadata + b'\n' + self.data))
        
        logger.info('Computing POW (difficulty: %s)...' % self.difficulty)

        self.mainHash = '0' * 64
        self.puzzle = self.mainHash[0:min(self.difficulty, len(self.mainHash))]
        self.shutdown = False
        self.payload = None

    def start(self):
        # Create a new thread for each subprocess
        for x in range(self.subproc_count):
            threading.Thread(target=self._spawn_proc).start()
        # Monitor the processes for a payload, shut them down when its found
        while True:
            if self.payload is None:
                time.sleep(0.1)
            else:
                self.shutdown = True
                return self.payload
    
    def _spawn_proc(self):
        # Create a child proof of work process, wait for data and send shutdown signal when its found
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
        nonce = -10000000 # Start nonce at negative 10 million so that the chosen nonce is likely to be small in length
        nonceStart = nonce
        data = self.data
        metadata = self.metadata
        puzzle = self.puzzle
        difficulty = self.difficulty
        mcore = core.Core() # I think we make a new core here because of multiprocess bugs
        while True:
            # Break if shutdown received
            if pipe.poll() and pipe.recv() == 'shutdown':
                break
            # Load nonce into block metadata
            metadata['pow'] = nonce
            # Serialize metadata, combine with block data
            payload = json.dumps(metadata).encode() + b'\n' + data
            # Check sha3_256 hash of block, compare to puzzle. Send payload if puzzle finished
            token = mcore._crypto.sha3Hash(payload)
            token = onionrutils.OnionrUtils.bytesToStr(token) # ensure token is string
            if puzzle == token[0:difficulty]:
                pipe.send(payload)
                break
            nonce += 1
        