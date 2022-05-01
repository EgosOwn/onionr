import os, uuid
TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

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
from filepaths import gossip_server_socket_file


BLOCK_MAX_SIZE = 1024 * 2000
BLOCK_MAX_SIZE_LEN = len(str(BLOCK_MAX_SIZE))
BLOCK_ID_SIZE = 128
BLOCK_STREAM_OFFSET_DIGITS = 8


class OnionrServerDiffuseTest(unittest.TestCase):


    def test_one_block(self):

        Thread(target=gossip_server, daemon=True).start()

        bl = onionrblocks.blockcreator.create_anonvdf_block(
            b"my test block", b"txt", 2800)
        blockdb.add_block_to_db(bl)

        async def diffuse_client():
            reader, writer = await asyncio.open_unix_connection(
                gossip_server_socket_file)
            writer.write(int(4).to_bytes(1, 'big'))
            await writer.drain()

            writer.write('0'.zfill(BLOCK_STREAM_OFFSET_DIGITS).encode('utf-8'))
            await writer.drain()

            self.assertEqual(bl.id, await reader.readexactly(BLOCK_ID_SIZE))

            # we want the block
            writer.write(int(1).to_bytes(1, 'big'))
            assert writer.drain()

            # check block size
            self.assertEqual(
                len(bl.raw),
                int((await reader.readexactly(BLOCK_MAX_SIZE_LEN)).decode('utf-8')))

            self.assertEqual(bl.raw, await reader.readexactly(len(bl.raw)))


        asyncio.run(diffuse_client())

unittest.main()
