#!/usr/bin/env python3
import sys, os
import time
sys.path.append(".")
sys.path.append("src/")
import uuid
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest, json

from utils import identifyhome, createdirs
from onionrsetup import setup_config
from utils import multiproc
createdirs.create_dirs()
setup_config()

class TestMultiProc(unittest.TestCase):
    def test_list_args(self):
        answer = multiproc.subprocess_compute(sum, 10, [1, 3])
        self.assertEqual(answer, 4)
    
    def test_two_args(self):
        def _add(a, b):
            return a + b
        answer = multiproc.subprocess_compute(_add, 10, 1, 3)
        self.assertEqual(answer, 4)
    
    def test_kwargs(self):
        def _add(a=0, b=0):
            return a + b
        answer = multiproc.subprocess_compute(_add, 10, a=1, b=3)
        self.assertEqual(answer, 4)
    
    def test_exception(self):
        def _fail():
            raise Exception("This always fails")
        with self.assertRaises(ChildProcessError):
            multiproc.subprocess_compute(_fail, 10)
    
    def test_delayed_exception(self):
        def _fail():
            time.sleep(3)
            raise Exception("This always fails")
        with self.assertRaises(ChildProcessError):
            multiproc.subprocess_compute(_fail, 10)
    
    def test_timeout(self):
        def _sleep():
            time.sleep(3)
        with self.assertRaises(TimeoutError):
            multiproc.subprocess_compute(_sleep, 1)
    
    def test_timeout_disabled(self):
        def _sleep():
            time.sleep(3)
        self.assertIsNone(multiproc.subprocess_compute(_sleep, -1))
        self.assertIsNone(multiproc.subprocess_compute(_sleep, 0))


unittest.main()
