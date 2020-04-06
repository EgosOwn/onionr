"""Onionr - Private P2P Communication.

LAN transport client thread
"""
from typing import List

import watchdog
from requests.exceptions import ConnectionError

from onionrcrypto.cryptoutils.randomshuffle import random_shuffle
from utils.bettersleep import better_sleep
from onionrutils.basicrequests import do_post_request, do_get_request
from threading import Thread
from onionrblocks import BlockList
from onionrblocks.blockimporter import import_block_from_data
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


class Client:
    def __init__(self):
        self.peers = []
        self.lookup_time = {}
        self.poll_delay = 10


    def get_lookup_time(self, peer):
        try:
            return self.lookup_time[peer]
        except KeyError:
            return 0

    def peer_work(self, peer):
        port = 1024

        self.peers.append(peer)
        for port in range(port, 65535):
            print(port)
            try:
                if do_get_request(f'http://{peer}:{port}/ping', proxyType='lan', ignoreAPI=True, connect_timeout=0.3) == 'onionr!':
                    port = port
                    print(f'{peer}:{port} found')
                    break
            except (AttributeError, ConnectionError):
                pass
        else:
            self.peers.remove(peer)
            return
        self.peers.append(peer)

        while True:
            block_list = self._too_many.get(BlockList).get()
            last_time = self.get_lookup_time(peer)
            new_blocks = set('\n'.join(do_get_request(f'http://{peer}:{port}/blist/{last_time}', proxyType='lan', ignoreAPI=True))) ^ set(block_list)

            for bl in new_blocks:
                import_block_from_data(
                    do_get_request(
                        f'http://{peer}:{port}/get/{bl}', proxyType='lan', ignoreAPI=True))
            better_sleep(10)
        self.peers.remove(peer)

    def connect_peer(self, peer):
        if peer in self.peers:
            return
        print(f'connecting to {peer}')
        Thread(target=self.peer_work, args=[peer], daemon=True).start()

