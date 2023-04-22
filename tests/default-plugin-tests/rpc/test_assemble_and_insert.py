import os, uuid
import base64
import secrets

import time
from nacl import signing

import kasten

TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

import unittest
import sys


import kasten
from kasten.generator import pack as kasten_pack

sys.path.append('static-data/official-plugins/rpc/rpc')
sys.path.append("src/")

import queue

import onionrblocks
from onionrblocks import generators
import mimcvdf

from gossip import blockqueues


import blocks

byte_cost = 10
second_cost = 4

def _get_rounds(seconds: int, size_bytes: int):
    return (seconds * second_cost) + (size_bytes * byte_cost)


class RPCAssembleAndInsertTest(unittest.TestCase):

    def test_assemble_and_insert(self):
        data = b'block data'
        metadata = {'ttl': 3600}
        kasten_packed = kasten_pack.pack(data, 'txt', metadata, int(time.time()))
        kasten_obj = kasten.Kasten('', kasten_packed, kasten.generator.KastenBaseGenerator, auto_check_generator=False)

        vdf_result = mimcvdf.vdf_create(kasten_packed, _get_rounds(3600, len(kasten_packed)))

        blocks.assemble_and_insert_block(base64.b64encode(kasten_packed), vdf_result)
        try:
            bl = blockqueues.gossip_block_queues[0].get_nowait()
            self.assertEqual(bl.data, data)
        except queue.Empty:
            bl = blockqueues.gossip_block_queues[1].get_nowait()
            self.assertEqual(bl.data, data)


unittest.main()
