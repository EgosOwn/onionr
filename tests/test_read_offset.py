#!/usr/bin/env python3
import sys, os
from time import sleep
import tempfile
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest, json

from utils import identifyhome, createdirs, readoffset
from onionrsetup import setup_config
createdirs.create_dirs()
setup_config()

class TestReadOffset(unittest.TestCase):
    def test_read_offset(self):
        temp = tempfile.mkstemp()[1]
        f = open(temp, 'wb')
        data = b"test1\ntest2\ntest3\test4"
        f.write(data)
        f.close()
        self.assertEqual(readoffset.read_from_offset(temp, 5).data, data[5:])
        self.assertEqual(readoffset.read_from_offset(temp, 5).new_offset, len(data))
        os.remove(temp)
    def test_read_whole(self):
        temp = tempfile.mkstemp()[1]
        f = open(temp, 'wb')
        data = b"test1\ntest2\ntest3\test4"
        f.write(data)
        f.close()
        self.assertEqual(readoffset.read_from_offset(temp).data, data)
        self.assertEqual(readoffset.read_from_offset(temp).new_offset, len(data))
        os.remove(temp)


unittest.main()
