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

sys.path.append('static-data/official-plugins/rpc/rpc')
sys.path.append("src/")

import queue

import onionrblocks

from gossip import blockqueues


import blocks

class MockQueue:
    def __init__(self):
        self.data = []
    def get_nowait(self):
        return self.data.pop(0)

    def put_nowait(self, data):
        print("putting", data)
        self.data.append(data)
        return True



class RPCInsertBlockTest(unittest.TestCase):

    def test_insert_block_dict_valid(self):
        bl = onionrblocks.create_anonvdf_block(b'test', 'test', 3600)
        insert_data = {
            'id': bl.id,
            'raw': base64.b64encode(bl.raw).decode('utf-8')
        }
        assert blocks.insert_block(insert_data) == "ok"
        try:
            blockqueues.gossip_block_queues[0].get_nowait()
        except queue.Empty:
            pass
        else:
            return
        bl = blockqueues.gossip_block_queues[1].get_nowait()
    
    def test_insert_block_dict_invalid(self):
        bl = onionrblocks.create_anonvdf_block(b'test', 'test', 3600)
        insert_data = {
            'id': secrets.token_hex(len(bl.id)),
            'raw': base64.b64encode(bl.raw).decode('utf-8')
        }
        try:
            blocks.insert_block(insert_data)
        except kasten.exceptions.InvalidID:
            pass
        try:
            blockqueues.gossip_block_queues[0].get_nowait()
        except queue.Empty:
            pass
        else:
            raise AssertionError("Block was inserted")
        try:
            blockqueues.gossip_block_queues[1].get_nowait()
        except queue.Empty:
            pass
        else:
            raise AssertionError("Block was inserted")
unittest.main()
