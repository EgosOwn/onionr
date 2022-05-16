import os, uuid
from unittest.mock import Mock
from time import sleep
import secrets


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


BLOCK_MAX_SIZE = 1024 * 2000
BLOCK_MAX_SIZE_LEN = len(str(BLOCK_MAX_SIZE))
BLOCK_ID_SIZE = 128
BLOCK_STREAM_OFFSET_DIGITS = 8
MAX_PEERS = 10
TRANSPORT_SIZE_BYTES = 64

class MockPeer(Peer):
    def __init__(self):
        self.transport_address = secrets.token_hex(16)
    def __hash__(self):
        return hash(self.transport_address)


class OnionrServerPeerAnnounce(unittest.TestCase):


    def test_peer_announce(self):

        Thread(target=gossip_server, daemon=True).start()
        sleep(0.03)

        address = MockPeer().transport_address

        async def announce_client():
            reader, writer = await asyncio.open_unix_connection(
                gossip_server_socket_file)
            writer.write(int(2).to_bytes(1, 'big'))
            await writer.drain()
            writer.write(address.encode('utf-8') + b'\n')
            await writer.drain()
            self.assertEqual(await reader.readexactly(1), int(1).to_bytes(1,'big'))

            try:
                await reader.readexactly(1)
            except asyncio.IncompleteReadError:
                pass
            else:
                raise AssertionError("Read past expected, announce stream must close after announce submission")


        asyncio.run(announce_client())

unittest.main()