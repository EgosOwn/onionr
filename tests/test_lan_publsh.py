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
import struct
from utils import bettersleep
from lan.discover import lan_ips, MCAST_GRP, MCAST_PORT, IS_ALL_GROUPS
from lan.discover import advertise_service
import socket
from socket import SHUT_RDWR
import logger
from etc import onionrvalues


class TestLanLearn(unittest.TestCase):
    def test_lan_broadcast(self):
        test_ip = '192.168.1.30'
        if onionrvalues.IS_QUBES:
            logger.info('Cannot run LAN tests on Qubes')
            return
        def multicast():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if IS_ALL_GROUPS:
                # on this port, receives ALL multicast groups
                sock.bind(('', MCAST_PORT))
            else:
                # on this port, listen ONLY to MCAST_GRP
                sock.bind((MCAST_GRP, MCAST_PORT))
            mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            service_ips = sock.recv(200).decode('utf-8')
            if not service_ips: raise ValueError

            self.assertIn('onionr', service_ips)
            self.assertEqual(len(set(set(service_ips.replace('onionr', '').split('-')) ^ set(lan_ips))), 1)
            for x in set(set(service_ips.replace('onionr', '').split('-')) ^ set(lan_ips)):
                self.assertEqual('', x)

            try:
                sock.shutdown(SHUT_RDWR)
            except OSError:
                pass
            sock.close()
        test_list = [test_ip]

        Thread(target=advertise_service, daemon=True).start()
        bettersleep.better_sleep(1)
        multicast()

unittest.main()
