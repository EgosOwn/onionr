import os, uuid
TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:12], os.path.basename(__file__)) + '/'
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
BLOCK_SIZE_LEN = len(str(BLOCK_MAX_SIZE))
BLOCK_ID_SIZE = 128
BLOCK_STREAM_OFFSET_DIGITS = 8


class OnionrDiffuseMany(unittest.TestCase):


    def test_many(self):

        Thread(target=gossip_server, daemon=True).start()
        blocks = []
        for _ in range(10):
            bl = onionrblocks.blockcreator.create_anonvdf_block(
                b"my test block" + os.urandom(16), b"txt", 2800)
            blockdb.add_block_to_db(bl)
            blocks.append(bl)

        async def diffuse_client():
            reader, writer = await asyncio.open_unix_connection(
                gossip_server_socket_file)

            # tell we want to stream blocks
            writer.write(int(4).to_bytes(1, 'big'))
            await writer.drain()

            # tell timestamp offset
            writer.write('0'.zfill(BLOCK_STREAM_OFFSET_DIGITS).encode('utf-8'))
            await writer.drain()

            # Read blocks from offset
            for i in range(10):
                bl_id = await reader.readexactly(BLOCK_ID_SIZE)
                for bl in blocks:
                    if bl.id == bl_id:
                        break

                # tell we want the block
                writer.write(int(1).to_bytes(1, 'big'))
                await writer.drain()

                # check block size
                self.assertEqual(
                    len(bl.raw),
                    int((await reader.readexactly(BLOCK_SIZE_LEN)).decode('utf-8')))

                self.assertEqual(bl.raw, await reader.readexactly(len(bl.raw)))
                writer.write(int(1).to_bytes(1, 'big'))
                await writer.drain()

            writer.write(int(0).to_bytes(1, 'big'))
            await writer.drain()


        asyncio.run(diffuse_client())

unittest.main()
