"""Onionr - Private P2P Communication.

Torgossip peer safedb interface
"""
from typing import TYPE_CHECKING
from base64 import b32decode
from struct import unpack, pack
frome time import time

from utils.identifyhome import identify_home
import safedb
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



class Peers:

    PACK_FORMAT = "qQ"

    def __init__(self, encrypt: bool):
        self.db = safedb.SafeDB(
            identify_home() + "/torgossip-peers.db", protected=encrypt)

    def _shrink_peer_address(self, peer):
        # strip .onion and b32decode peer address for lower database mem usage
        if len(peer) == 62:  # constant time
            return b32decode(peer[:-6])  # O(N)
        return peer

    def _pack_and_store_info(self, peer, new_score=None, new_seen=None):
        # Repack peer information with new value(s) and store it
        score, seen = unpack(self.PACK_FORMAT, self.db.get(
            self._shrink_peer_address(peer)))

        if new_score:
            score = new_score
        if new_seen:
            seen = new_seen

        self.db.put(peer, pack(self.PACK_FORMAT, score, seen))

    def add_score(self, peer, new_score):
        shrunk = self._shrink_peer_address(peer)
        score, _ = unpack("qQ", self.db.get(shrunk))

        self._pack_and_store_info(
            shrunk, new_score=score + new_score)

    def update_seen(self, peer):
        peer = self._shrink_peer_address(peer)
        _pack_and_store_info(peer, new_seen=int(time()))



