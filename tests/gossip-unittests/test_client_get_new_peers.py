import os, uuid
from sqlite3 import Time
import socket
from queue import Queue
from time import sleep, time
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
from gossip.client import get_new_peers
from gossip.peerset import gossip_peer_set


BLOCK_MAX_SIZE = 1024 * 2000
BLOCK_MAX_SIZE_LEN = len(str(BLOCK_MAX_SIZE))
BLOCK_ID_SIZE = 128
BLOCK_STREAM_OFFSET_DIGITS = 8
MAX_PEERS = 10
TRANSPORT_SIZE_BYTES = 64

server_file = TEST_DIR + 'test_serv.sock'

class MockPeer:
    def __init__(self):
        self.transport_address = secrets.token_hex(16)
    def __hash__(self):
        return hash(self.transport_address)

    def get_socket(self, timeout):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(server_file)
        return s

fake_peer_addresses = [MockPeer().transport_address for i in range(10)]


def _server():

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(server_file)
        s.listen(1)
        conn, _ = s.accept()
        with conn:
            conn.recv(1)
            for address in fake_peer_addresses:
                conn.sendall(address.encode('utf-8') + b'\n')
    try:
        os.remove(server_file)
    except FileNotFoundError:
        pass




class OnionrGossipClientGetNewPeers(unittest.TestCase):

    def test_get_new_peers_no_peers(self):
        gossip_peer_set.clear()
        self.assertRaises(ValueError, get_new_peers)
        self.assertFalse(len(gossip_peer_set))


    def test_get_new_peers(self):
        Thread(target=_server, daemon=True).start()
        sleep(1)
        p = MockPeer()
        gossip_peer_set.clear()
        gossip_peer_set.add(p)
        get_new_peers()
        assert len(gossip_peer_set)
        self.assertTrue(len(gossip_peer_set), len(fake_peer_addresses) + 1)

    def test_peer_too_long(self):
        Thread(target=_server, daemon=True).start()
        sleep(1)
        gossip_peer_set.clear()
        fake_peer_addresses.pop()
        peer_good = MockPeer()
        p = MockPeer()
        p.transport_address = secrets.token_hex(12)
        fake_peer_addresses.append(p.transport_address)
        gossip_peer_set.append(peer_good)
        get_new_peers()
        self.assertNotIn(p, gossip_peer_set)


sleep(0.5)
unittest.main()
