#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import uuid
from threading import Thread
TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import unittest, json

from utils import identifyhome, createdirs
from onionrsetup import setup_config
createdirs.create_dirs()
setup_config()
from utils import bettersleep
from lan.discover import lan_ips, MCAST_GRP, MCAST_PORT
from lan.discover import learn_services, advertise_service
import socket
from socket import SHUT_RDWR
lan_ips = ['']


class TestLanLearn(unittest.TestCase):
    def test_lan_learn(self):
        test_ip = '192.168.1.30'
        def multicast():
            port = 1349
            MULTICAST_TTL = 3
            ips = '-'.join([test_ip]) + f'-{port}'

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
            sock.sendto(f"onionr-{ips}".encode('utf-8'), (MCAST_GRP, MCAST_PORT))
            bettersleep.better_sleep(1)
            try:
                sock.shutdown(SHUT_RDWR)
            except OSError:
                pass
            sock.close()
        test_list = [test_ip]

        Thread(target=learn_services, daemon=True).start()
        bettersleep.better_sleep(3)
        multicast()
        self.assertIn(test_ip, test_list)

unittest.main()
