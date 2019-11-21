#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
from utils import identifyhome

class IdentifyHomeTest(unittest.TestCase):
    def test_standard_linux(self):
        del os.environ["ONIONR_HOME"]
        self.assertEqual(identifyhome.identify_home(), os.path.expanduser('~') + '/.local/share/onionr/')
    def test_environ(self):
        os.environ["ONIONR_HOME"] = "testhome"
        self.assertEqual(os.getcwd() + "/testhome/", identifyhome.identify_home())

unittest.main()
