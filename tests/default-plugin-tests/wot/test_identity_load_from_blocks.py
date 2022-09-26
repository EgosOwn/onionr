import dbm
import os, uuid

import time

TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
os.makedirs(TEST_DIR)

import unittest
import sys
sys.path.append('static-data/official-plugins/wot/wot')
sys.path.append("src/")
import onionrblocks
from blockdb import block_db_path
from identity import Identity
from loadfromblocks import load_identities_from_blocks
import blockdb


def _safe_remove(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


class LoadIdentitiesFromBlocksTest(unittest.TestCase):

    def test_load_from_blocks_no_blocks(self):
        _safe_remove(block_db_path)
        self.assertEqual(len(list(load_identities_from_blocks())), 0)

    def test_load_from_blocks_one(self):
        _safe_remove(block_db_path)

        serialized_identity = b'jp\x18\xccB\xbb\xb5T\xae%\xc2NfvF\xd9e\xdb\xd1\x11\x13\x8al\x9f\x9d\xb7/\xc5\x0eG\xe9g{f\xa2\n\r\xe3cK\x96E\x01d\xbbz\xb5\xb1\x1eRA`\x94\xab\xf2\n",\xfe\xca\x0b\xb4v\x0500000000000000000test\x1b\xc8\x8d\x88\xe39\xeb\xbe\\\xbd\xc8[xD\xbcr\x1f\xa4\x03%p\x19\xf7\xd7%6S\xef*\x03\x91\xe31662057071'

        bl = onionrblocks.create_anonvdf_block(
            serialized_identity, b'wotb', 3600)

        with dbm.open(block_db_path, 'c') as db:
            db[bl.id] = bl.raw

        self.assertEqual(len(list(load_identities_from_blocks())), 1)

    def test_load_from_blocks_one_invalid(self):
        _safe_remove(block_db_path)
        serialized_identity_invalid = b'jp\x18\xccB\xbb\xb5T\xae%\xc2NfvF\xd9e\xdb\xd1\x12\x14\x8al\x9f\x9d\xb7/\xc5\x0eG\xe9g{f\xa2\n\r\xe3cK\x96E\x01d\xbbz\xb5\xb1\x1eRA`\x94\xab\xf2\n",\xfe\xca\x0b\xb4v\x0500000000000000000test\x1b\xc8\x8d\x88\xe39\xeb\xbe\\\xbd\xc8[xD\xbcr\x1f\xa4\x03%p\x19\xf7\xd7%6S\xef*\x03\x91\xe31662057071'
        bl = onionrblocks.create_anonvdf_block(
            serialized_identity_invalid, b'wotb', 3600)

        with dbm.open(block_db_path, 'c') as db:
            db[bl.id] = bl.raw

        self.assertEqual(len(list(load_identities_from_blocks())), 0)


unittest.main()
