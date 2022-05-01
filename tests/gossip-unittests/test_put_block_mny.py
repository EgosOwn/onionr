import os, uuid
from queue import Empty
TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:5], os.path.basename(__file__)) + '/'
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
BLOCK_MAX_SIZE_LEN = len(str(BLOCK_MAX_SIZE))
BLOCK_ID_SIZE = 128
BLOCK_STREAM_OFFSET_DIGITS = 8


class OnionrServerPutBlocksTest(unittest.TestCase):


    def test_put_blocks(self):

        Thread(target=gossip_server, daemon=True).start()
        sleep(0.01)

        blocks = []
        for _ in range(10):
            bl = onionrblocks.blockcreator.create_anonvdf_block(
                b"my test block" + os.urandom(16), b"txt", 2800)
            blockdb.add_block_to_db(bl)
            blocks.append(bl)

        async def blocks_put_client():
            reader, writer = await asyncio.open_unix_connection(
                gossip_server_socket_file)
            writer.write(int(5).to_bytes(1, 'big'))
            await writer.drain()

            for bl in blocks:
                writer.write(bl.id)
                writer.write(
                    str(len(bl.raw)).zfill(BLOCK_MAX_SIZE_LEN).encode('utf-8'))
                writer.write(bl.raw)
                await writer.drain()

                sleep(0.03)
                try:
                    self.assertEqual(gossip_block_queues[0].get_nowait().raw, bl.raw)
                except Empty:
                    self.assertEqual(gossip_block_queues[1].get_nowait().raw, bl.raw)


        asyncio.run(blocks_put_client())

unittest.main()
