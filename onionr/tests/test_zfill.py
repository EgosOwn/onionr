#!/usr/bin/env python3
import unittest, sys
sys.path.append(".")

from utils import reconstructhash

class ZFill_Hash(unittest.TestCase):
    def test_reconstruct(self):
        h = b"4d20d791cbc293999b97cc627aa011692d317dede3d0fbd390c763210b0d"
        self.assertEqual(reconstructhash.reconstruct_hash(h), b"0000" + h)
        h = b"4d20d791cbc293999b97cc627aa011692d317dede3d0fbd390c763210b0d"
        self.assertEqual(reconstructhash.reconstruct_hash(h, 62), b"00" + h)
    
    def test_deconstruct(self):
        h = b"0000e918d24999ad9b0ff00c1d414f36b74afc93871a0ece4bd452f82b56af87"
        h_no = b"e918d24999ad9b0ff00c1d414f36b74afc93871a0ece4bd452f82b56af87"
        self.assertEqual(reconstructhash.deconstruct_hash(h), h_no)
        h = "0000e918d24999ad9b0ff00c1d414f36b74afc93871a0ece4bd452f82b56af87"
        h_no = "e918d24999ad9b0ff00c1d414f36b74afc93871a0ece4bd452f82b56af87"
        self.assertEqual(reconstructhash.deconstruct_hash(h), h_no)
unittest.main()