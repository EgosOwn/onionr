#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
import ipaddress
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest

from lan.getip import lan_ips

class TestGetLanIps(unittest.TestCase):
    def test_get_lan_ips(self):
        self.assertGreater(len(lan_ips), 0)
        for ip in lan_ips:
            ip = ipaddress.IPv4Address(ip)
            if not ip.is_private or ip.is_multicast or ip.is_reserved:
                raise ValueError


unittest.main()
