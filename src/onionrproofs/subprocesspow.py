#!/usr/bin/env python3
"""Onionr - Private P2P Communication.

Multiprocess proof of work
"""

import os
from multiprocessing import Pipe, Process
import threading
import time
import secrets

import onionrproofs

import ujson as json

import logger
from onionrutils import bytesconverter
from onionrcrypto.hashers import sha3_hash

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


class SubprocessPOW:
    def __init__(self, data, metadata, subproc_count=None):
        """
            Onionr proof of work using multiple processes
            Accepts block data, block metadata
            if subproc_count is not set,
            os.cpu_count() is used to determine the number of processes

            Due to Python GIL multiprocessing/use of external libraries
            is necessary to accelerate CPU bound tasks
        """
        # No known benefit to using more processes than there are cores.
        # Note: os.cpu_count perhaps not always accurate
        if subproc_count is None:
            subproc_count = os.cpu_count()
        self.subproc_count = subproc_count
        self.result = ''
        self.shutdown = False
        self.data = data
        self.metadata = metadata

        """dump dict to measure bytes of json metadata
        Cannot reuse later bc the pow token must be added
        """
        json_metadata = json.dumps(metadata).encode()

        self.data = bytesconverter.str_to_bytes(data)

        compiled_data = bytes(json_metadata + b'\n' + self.data)

        # Calculate difficulty. May use better algorithm in the future.
        self.difficulty = onionrproofs.getDifficultyForNewBlock(compiled_data)

        logger.info('Computing POW (difficulty: %s)...' % (self.difficulty,))

        self.main_hash = '0' * 64
        self.puzzle = self.main_hash[0:min(self.difficulty,
                                           len(self.main_hash))]
        self.shutdown = False
        self.payload = None

    def start(self):
        """spawn the multiproc handler threads"""
        # Create a new thread for each subprocess
        for _ in range(self.subproc_count): # noqa
            threading.Thread(target=self._spawn_proc, daemon=True).start()
        # Monitor the processes for a payload, shut them down when its found
        while True:
            if self.payload is None:
                time.sleep(0.1)
            else:
                self.shutdown = True
                return self.payload

    def _spawn_proc(self):
        """Create a child proof of work process
        wait for data and send shutdown signal when its found"""
        # The importerror started happening in 3.9.x
        # not worth fixing because this POW will be replaced by VDF
        try:
            parent_conn, child_conn = Pipe()
            p = Process(target=self.do_pow, args=(child_conn,), daemon=True)
            p.start()
        except ImportError:
            logger.error(
                "Error in subprocess module when getting new POW " +
                "pipe.\nThis is related to a problem in 3.9.x", terminal=True)
            return
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
            p.terminate()
            self.payload = payload

    def do_pow(self, pipe):
        """find partial hash colision generating nonce for a block"""
        nonce = 0
        data = self.data
        metadata = self.metadata
        metadata['n'] = secrets.randbits(16)
        puzzle = self.puzzle
        difficulty = self.difficulty
        try:
            while True:
                #logger.info('still running', terminal=True)
                # Break if shutdown received
                try:
                    if pipe.poll() and pipe.recv() == 'shutdown':
                        break
                except KeyboardInterrupt:
                    break
                # Load nonce into block metadata
                metadata['c'] = nonce
                # Serialize metadata, combine with block data
                payload = json.dumps(metadata).encode() + b'\n' + data
                # Check sha3_256 hash of block, compare to puzzle
                # Send payload if puzzle finished
                token = sha3_hash(payload)
                # ensure token is string
                token = bytesconverter.bytes_to_str(token)
                if puzzle == token[0:difficulty]:
                    pipe.send(payload)
                    break
                nonce += 1
        except KeyboardInterrupt:
            pass
