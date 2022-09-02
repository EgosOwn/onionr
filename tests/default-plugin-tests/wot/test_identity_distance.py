import os, uuid
from random import randint
from time import sleep
import secrets


TEST_DIR = 'testdata/%s-%s' % (str(uuid.uuid4())[:6], os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

import unittest
import sys
sys.path.append(".")
sys.path.append('static-data/default-plugins/wot/wot')
sys.path.append("src/")
from identity import Identity, get_distance


def generate_graph(iden: Identity, depth, max_neighbors):
    c = 0
    if depth == 0:
        return
    for i in range(randint(0, max_neighbors)):
        i = Identity(os.urandom(32), "1" + secrets.token_hex(4))
        iden.trusted.add(i)
        generate_graph(i, depth - 1, max_neighbors)


class IdentityDistanceTest(unittest.TestCase):
    def test_distance(self):
        iden = Identity(os.urandom(32), "1" + secrets.token_hex(4))
        generate_graph(iden, 10, 5)
        iden2 = list(list(iden.trusted)[0].trusted)[0]

        self.assertEqual(get_distance(iden, iden2), 2)

unittest.main()
