"""Onionr - Private P2P Communication.

NetUtils offers various useful functions to Onionr networking.
"""
from random import SystemRandom

from onionrutils import basicrequests
from .readstatic import read_static
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


def check_network(torPort=0) -> bool:
    """Check if we are connected to the internet (through Tor)."""
    success = False
    try:
        connect_urls = read_static('connect-check.txt').split(',')
        SystemRandom().shuffle(connect_urls)

        for url in connect_urls:
            if basicrequests.do_get_request(
                    url, port=torPort, ignoreAPI=True) is not False:
                success = True
                break
    except FileNotFoundError:
        pass
    return success
