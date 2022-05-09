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

import onionrblocks


from filepaths import gossip_server_socket_file
from gossip.client import block_queue_processing
from gossip import client
from gossip.blockqueues import gossip_block_queues
from gossip.peerset import gossip_peer_set


BLOCK_MAX_SIZE = 1024 * 2000
BLOCK_MAX_SIZE_LEN = len(str(BLOCK_MAX_SIZE))
BLOCK_ID_SIZE = 128
BLOCK_STREAM_OFFSET_DIGITS = 8
MAX_PEERS = 10
TRANSPORT_SIZE_BYTES = 64

server_file = TEST_DIR + 'test_serv.sock'


def gen_random_block():
    return onionrblocks.create_anonvdf_block(os.urandom(12), b'txt', 3600)


test_blocks = []

test_thread = []

test_block_count = 5
for i in range(test_block_count):
    test_blocks.append(gen_random_block())


class MockPeer:
    def __init__(self):
        self.transport_address = secrets.token_hex(16)
    def __hash__(self):
        return hash(self.transport_address)


    def get_socket(self, timeout):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(server_file)
        return s

class MockPhase:
    def __init__(self):
        return
    def remaining_time(self):
        return 120
    def is_stem_phase(self):
        return False


class OnionrGossipClientBlockChoice(unittest.TestCase):


    @patch('gossip.client.dandelionstem.stem_out')
    @patch('gossip.client.store_blocks')
    def test_client_block_processing_fluff_phase(self, mock_store_blocks, mock_stem_out):
        gossip_peer_set.add(MockPeer())

        client.dandelion_phase = MockPhase()
        block_queue_processing()
        self.assertTrue(mock_store_blocks.called)


unittest.main()
