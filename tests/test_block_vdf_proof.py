#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest, json

from utils import identifyhome, createdirs
from onionrsetup import setup_config
from onionrproofs import vdf
from time import time

createdirs.create_dirs()
setup_config()

class TestVdf(unittest.TestCase):
    def test_vdf(self):
        res = vdf.create(b'test')
        int(res, 16)
        if len(res) == 0: raise ValueError
        self.assertEqual(vdf.multiprocess_create(b'test'), res)
    def test_speed(self):
        t = time()
        vdf.create(b'test')
        self.assertTrue(time() - t <= 10)
        # test 2 kb
        t = time()
        vdf.create(b't'*2000)
        self.assertTrue(time() - t >= 10)
        #timeit(lambda: vdf.create(b'test'))


unittest.main()
