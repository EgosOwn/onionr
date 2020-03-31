"""Onionr - Private P2P Communication.

LAN transport client thread
"""
from typing import List

from onionrcrypto.cryptoutils.randomshuffle import random_shuffle
from utils.bettersleep import better_sleep
from onionrutils.basicrequests import do_post_request, do_get_request
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

    def start(self):
        while True:
            self.peers = random_shuffle(self.peers)



            better_sleep(self.pull_delay)

