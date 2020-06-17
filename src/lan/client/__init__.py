"""Onionr - Private P2P Communication.

LAN transport client thread
"""
import requests

from typing import Set

from onionrtypes import LANIP
from utils.bettersleep import better_sleep

from threading import Thread
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

connected_lan_peers: Set[LANIP] = set([])


def _lan_work(peer: LANIP):
    identified_port = lambda: None
    identified_port.port = 0
    def find_port(start=1024, max=0):
        for i in range(start, 65535):
            if i > max and max > 0:
                break
            if identified_port.port != 0:
                break
            try:
                if requests.get(f'http://{peer}:{i}/ping', timeout=1) == 'onionr!':
                    print("Found", peer, i)
                    identified_port.port = i
                    break
            except requests.exceptions.ConnectionError:
                pass
    
    Thread(target=find_port, args=[1024, 32767], daemon=True).start()
    Thread(target=find_port, args=[32767, 65535], daemon=True).start()
    while identified_port.port == 0:
        better_sleep(1)
    print(LANIP, identified_port.port)


def connect_peer(peer: LANIP):
    Thread(target=_lan_work, args=[peer], daemon=True).start()
    connected_lan_peers.add(peer)
