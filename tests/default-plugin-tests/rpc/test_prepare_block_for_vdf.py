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

from gossip import blockqueues


import blocks

byte_cost = 10
second_cost = 4

def _get_rounds(seconds: int, size_bytes: int):
    return (seconds * second_cost) + (size_bytes * byte_cost)

class RPCPrepareBlockForVDFTest(unittest.TestCase):

    def test_prepare_block_for_vdf(self):
        data_bytes = b'block data'
        data = base64.b64encode(data_bytes)

        resp_dict = blocks.prepare_block_for_vdf(data, 'txt', 3600, {})
        expected_kasten_packed = kasten_pack.pack(data_bytes, 'txt', {'ttl': 3600}, int(time.time()))
        expected_kasten_obj = kasten.Kasten('', expected_kasten_packed, kasten.generator.KastenBaseGenerator, auto_check_generator=False)
        self.assertTrue(resp_dict['raw'])
        self.assertEqual(base64.b64decode(resp_dict['raw']),expected_kasten_packed)
        self.assertEqual(resp_dict['rounds_needed'], _get_rounds(3600, len(expected_kasten_obj.get_packed())))



unittest.main()
