"""
Onionr Vanity address generator

Library to generate vanity ed25519 addresses in various encodings
"""
"""
Onionr Vanity Address Generator
Copyright (C) 2019 Kevin Froman

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

import niceware
import nacl.signing, nacl.encoding

import multiprocessing
from multiprocessing import Process, Pipe, Queue
import re, time
import threading

import logger

wordlist = niceware.WORD_LIST

def find_vanity_mnemonic(start_words: str, queue):
    key_pair = [b"", b""]
    vanity_key = ""
    check = 0
    while not vanity_key.startswith(start_words):
        key = nacl.signing.SigningKey.generate()
        key_pair[1] = key.encode(nacl.encoding.RawEncoder)
        key_pair[0] = key.verify_key.encode(encoder=nacl.encoding.RawEncoder)
        vanity_key = '-'.join(niceware.bytes_to_passphrase(key_pair[0]))
        check += 1
    else:
        queue.put(key_pair)
    return key_pair

def _start(start_words, obj):
    done = False
    try:
        q = Queue()
        p = Process(target=find_vanity_mnemonic, args=[start_words, q], daemon=True)
        p.daemon = True
        p.start()
    except ImportError:
        logger.error(
            "Error in subprocess module when getting new POW " +
            "pipe.\nThis is related to a problem in 3.9.x", terminal=True)
        return
    rec = None
    while not done:
        try:
            if rec == None:
                rec = q.get(True, 1)
        except:
            rec = None
        if rec != None or obj.done:
            done = True
            obj.done = True
            obj.result = rec
    return rec

def handler(start_words: str):
    obj = lambda test: None
    obj.done = False
    for x in range(multiprocessing.cpu_count()):
        threading.Thread(target=_start, args=[start_words, obj], daemon=True).start()
    while not obj.done:
        time.sleep(1)
    return obj.result

def find_multiprocess(start_words: str):
    start_words = start_words.strip()
    start_words = re.sub(' +', ' ', start_words)
    test_words = str(start_words)

    for word in test_words.split(' '):
        for validword in wordlist:
            if word == validword:
                break
        else:
            raise ValueError('%s not in wordlist' % (word,))
    return handler(start_words)
