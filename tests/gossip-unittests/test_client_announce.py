import os, uuid
from unittest.mock import Mock
from time import sleep
import secrets
import socket

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
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
from gossip.server import gossip_server
from gossip.peer import Peer


from filepaths import gossip_server_socket_file
from gossip.peerset import gossip_peer_set
from gossip.client.announce import do_announce


BLOCK_MAX_SIZE = 1024 * 2000
BLOCK_SIZE_LEN = len(str(BLOCK_MAX_SIZE))
BLOCK_ID_SIZE = 128
BLOCK_STREAM_OFFSET_DIGITS = 8
MAX_PEERS = 10
TRANSPORT_SIZE_BYTES = 64

class MockPeer(Peer):
    def __init__(self):
        self.transport_address = secrets.token_hex(16)
    def __hash__(self):
        return hash(self.transport_address)
    def get_socket(self, timeout):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(30)
        s.connect(server_file)
        return s

server_file = TEST_DIR + 'test_serv.sock'

reced_address = ['']

def _announce_server():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(server_file)
        while True:

            s.listen(1)
            conn, _ = s.accept()

            with conn:
                conn.recv(1)
                for _ in range(TRANSPORT_SIZE_BYTES):
                    dat = conn.recv(1).decode('utf-8')
                    if dat == '\n':
                        conn.sendall(int(1).to_bytes(1, 'big'))
                        break
                    reced_address[0] += dat
                else:
                    conn.sendall(int(0).to_bytes(1, 'big'))



Thread(target=_announce_server, daemon=True).start()


class OnionrClientAnnounce(unittest.TestCase):

    def test_client_announce_too_long(self):
        import onionrplugins

        our_address = "testtransport" * 100

        def event_func(event, *args, data={}, **kwargs):
            data['callback'](data['peer'], "testtransport" * 100)

        onionrplugins.events.event = event_func

        reced_address[0] = ''
        gossip_peer_set.clear()
        p = MockPeer()
        gossip_peer_set.append(p)

        do_announce()
        self.assertNotEqual(our_address, reced_address[0])

    def test_client_announce(self):
        import onionrplugins

        our_address = "testtransport"

        def event_func(event, *args, data={}, **kwargs):
            data['callback'](data['peer'], "testtransport")

        onionrplugins.events.event = event_func

        gossip_peer_set.clear()
        reced_address[0] = ''
        p = MockPeer()
        gossip_peer_set.append(p)

        do_announce()
        self.assertEqual(our_address, reced_address[0])



unittest.main()
