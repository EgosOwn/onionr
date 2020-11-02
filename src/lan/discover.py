"""Onionr - Private P2P Communication.

Discover and publish private-network
"""
import socket
import struct
from ipaddress import ip_address

from .getip import lan_ips, best_ip
from utils.bettersleep import better_sleep
from . import client
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
MCAST_GRP = '224.0.0.112'
MCAST_PORT = 1337
IS_ALL_GROUPS = True
ANNOUNCE_LOOP_SLEEP = 30


def learn_services():
    """Take a list to infintely add lan service info to."""

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

    while True:
        service_ips = sock.recv(200).decode('utf-8')
        if 'onionr' not in service_ips:
            continue
        service_ips = service_ips.replace('onionr-', '').split('-')

        for service in service_ips:
            try:
                ip_address(service)
                if not ip_address(service).is_private:
                    raise ValueError
                if service in lan_ips:
                    raise ValueError
            except ValueError:
                pass
            else:
                client.connect_peer(service)


def advertise_service(specific_ips=None):
    # regarding socket.IP_MULTICAST_TTL
    # ---------------------------------
    # for all packets sent, after three hops on the network the packet will not
    # be re-sent/broadcast
    # (see https://www.tldp.org/HOWTO/Multicast-HOWTO-6.html)
    MULTICAST_TTL = 3

    ips = best_ip
    if not ips:
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    while True:
        sock.sendto(f"onionr-{ips}".encode('utf-8'), (MCAST_GRP, MCAST_PORT))
        better_sleep(ANNOUNCE_LOOP_SLEEP)

