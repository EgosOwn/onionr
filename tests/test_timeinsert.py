#!/usr/bin/env python3
import unittest, sys
sys.path.append(".")
sys.path.append("src/")

from onionrblocks import time_insert
from onionrblocks import onionrblockapi

class TestTimeInsert(unittest.TestCase):
    def test_time_insert_none(self):
        bl = time_insert('test')
        self.assertTrue(bl)
        bl = onionrblockapi.Block(bl)
        self.assertIs(bl.bmetadata['dly'], 0)

    def test_time_insert_10(self):
        bl = time_insert('test', delay=10)
        self.assertTrue(bl)
        bl = onionrblockapi.Block(bl)
        self.assertIs(bl.bmetadata['dly'], 10)

    def test_negative(self):
        self.assertRaises(ValueError, time_insert, 'test', delay=-1)
        self.assertRaises(ValueError, time_insert, 'test', delay=-10)



unittest.main()
