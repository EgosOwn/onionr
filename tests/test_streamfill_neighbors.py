#!/usr/bin/env python3
import sys, os
import subprocess
sys.path.append(".")
sys.path.append("src/")
import uuid
import binascii
from base64 import b32decode
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest

from streamfill import identify_neighbors, extract_ed25519_from_onion_address

class TestStreamfillNeighbors(unittest.TestCase):
    def test_neighbor_closeness_consistent(self):
        main = '7uifxsgidchopmdwmtip6x4ydra6cpf2ov4ghj2lzx5uydyssduh5qid.onion'
        others = ['bxxajpimlonmbxb5jzjre3go3dvfobqyayqwpksd6zpjz4s4mknstwyd.onion', '2zofaifd6s3flwbv5wl4vtgnesbprc4f2ptljl4a47dfkvrbmw3e5iqd.onion', '6umslj7jtzu27n4jgf3byn55ztz5mkoqocx32zwjya6rbnxqjpyysyyd.onion']
        main_num = int.from_bytes(extract_ed25519_from_onion_address(main), 'big')

        test_data = identify_neighbors(main, others, 3)

        my_result = []
        for i in others:
            my_result.append((i, abs(main_num - int.from_bytes(extract_ed25519_from_onion_address(i), 'big'))))
        my_result.sort(key=lambda p: p[1])

        final = []
        for i in my_result:
            final.append(i[0])
        self.assertListEqual(final, test_data)


    def test_neighbor_closeness_random(self):
        onions = []
        p = subprocess.Popen(["scripts/generate-onions.py", '100'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        for line in iter(p.stdout.readline, b''):
            line = line.decode()
            onions.append(line.strip())
        p.terminate()
        main = '7uifxsgidchopmdwmtip6x4ydra6cpf2ov4ghj2lzx5uydyssduh5qid.onion'
        main_num = int.from_bytes(extract_ed25519_from_onion_address(main), 'big')

        test_data = identify_neighbors(main, onions, 100)

        my_result = []
        for i in onions:
            my_result.append((i, abs(main_num - int.from_bytes(extract_ed25519_from_onion_address(i), 'big'))))
        my_result.sort(key=lambda p: p[1])

        final = []
        for i in my_result:
            final.append(i[0])
        self.assertListEqual(final, test_data)


unittest.main()
