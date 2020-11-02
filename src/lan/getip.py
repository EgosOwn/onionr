"""Onionr - Private P2P Communication.

Identify LAN ip addresses and determine the best one
"""
from ipaddress import IPv4Address

from psutil import net_if_addrs
from socket import AF_INET

import logger
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

lan_ips = []

# https://psutil.readthedocs.io/en/latest/#psutil.net_if_addrs
def _get_lan_ips():
    for interface in net_if_addrs().keys():
        for address in net_if_addrs()[interface]:
            # Don't see benefit in ipv6, so just check for v4 addresses
            if address[0] == AF_INET:
                # Mark the address for use in LAN if it is a private address
                if IPv4Address(address[1]).is_private and not IPv4Address(address[1]).is_loopback:
                    lan_ips.append(address[1])
try:
    _get_lan_ips()
except OSError:
    logger.warn("Could not identify LAN ips due to OSError.")

# These are more likely to be actual local subnets rather than VPNs
for ip in lan_ips:
    if '192.168' in ip:
        best_ip = ip
        break
else:
    try:
        best_ip = lan_ips[0]
    except IndexError:
        best_ip = ""
