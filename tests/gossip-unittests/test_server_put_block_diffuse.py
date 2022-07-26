import os, uuid
from queue import Empty
TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

from time import sleep
from threading import Thread
import asyncio
import unittest
import sys
sys.path.append(".")
sys.path.append("src/")

from ordered_set import OrderedSet
import onionrblocks

import blockdb
from gossip.server import gossip_server
from gossip.blockqueues import gossip_block_queues
from filepaths import gossip_server_socket_file


BLOCK_MAX_SIZE = 1024 * 2000
BLOCK_SIZE_LEN = len(str(BLOCK_MAX_SIZE))
BLOCK_ID_SIZE = 128
BLOCK_STREAM_OFFSET_DIGITS = 8


class OnionrServerPutBLTestDiffuse(unittest.TestCase):


    def test_put_block(self):

        Thread(target=gossip_server, daemon=True).start()
        sleep(0.01)

        bl = onionrblocks.blockcreator.create_anonvdf_block(
            b"my test block", b"txt", 2800)

        async def block_put_client():
            reader, writer = await asyncio.open_unix_connection(
                gossip_server_socket_file)
            writer.write(int(6).to_bytes(1, 'big'))
            writer.write(bl.id)

            self.assertEqual(int.from_bytes(await reader.readexactly(1), 'big'), 1)
            writer.write(
                str(len(bl.raw)).zfill(BLOCK_SIZE_LEN).encode('utf-8'))
            writer.write(bl.raw)
            sleep(0.2)
            self.assertIn(bl.id, list([block.id for block in blockdb.get_blocks_after_timestamp(0)]))
            await writer.drain()


        asyncio.run(block_put_client())

unittest.main()
