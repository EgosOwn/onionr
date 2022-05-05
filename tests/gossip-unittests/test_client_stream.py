import os, uuid
from sqlite3 import Time
import socket
from queue import Queue
from time import sleep
import secrets


TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

from threading import Thread
import asyncio
import unittest
import sys
sys.path.append(".")
sys.path.append("src/")
from unittest.mock import patch

from ordered_set import OrderedSet
from gossip import peerset


import onionrblocks

import blockdb

from gossip.peerset import gossip_peer_set
from gossip.client import stream_from_peers



from filepaths import gossip_server_socket_file


BLOCK_MAX_SIZE = 1024 * 2000
BLOCK_MAX_SIZE_LEN = len(str(BLOCK_MAX_SIZE))
BLOCK_ID_SIZE = 128
BLOCK_STREAM_OFFSET_DIGITS = 8
MAX_PEERS = 10
TRANSPORT_SIZE_BYTES = 64

server_file = TEST_DIR + 'test_serv.sock'

def _server():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(server_file)
        s.listen(1)
        conn, _ = s.accept()
        with conn:
            while True:
                conn.recv(1)
                conn.recv(BLOCK_STREAM_OFFSET_DIGITS)
                for bl in test_blocks:
                    conn.sendall(bl.id)
                    conn.recv(1)
                    conn.sendall(str(len(bl.raw)).encode('utf-8').zfill(BLOCK_MAX_SIZE_LEN))
                    conn.sendall(bl.raw)
                    conn.recv(1)

def gen_random_block():
    return onionrblocks.create_anonvdf_block(os.urandom(12), b'txt', 3600)

test_blocks = []

test_block_count = 5
for i in range(test_block_count):
    test_blocks.append(gen_random_block())


Thread(target=_server, daemon=True).start()

class MockPeer:
    def __init__(self):
        self.transport_address = secrets.token_hex(16)
    def __hash__(self):
        return hash(self.transport_address)


    def get_socket(self, timeout):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(server_file)
        return s



class OnionrGossipClientDiffuse(unittest.TestCase):


    def test_client_stream(self):
        gossip_peer_set.add(MockPeer())
        Thread(target=stream_from_peers, daemon=True).start()

        c = 0
        while c < 60:
            c += 1
            if len(list(blockdb.get_blocks_after_timestamp(0))) == test_block_count:
                break
            sleep(1)
        else:
            raise TimeoutError("Did not stream blocks in time")


unittest.main()
