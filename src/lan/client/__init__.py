"""Onionr - Private P2P Communication.

LAN transport client thread
"""
import requests

from typing import Set

from onionrtypes import LANIP
import logger
from coredb.blockmetadb import get_block_list
from onionrblocks.blockimporter import import_block_from_data
import onionrexceptions
from ..server import ports
from onionrproofs import hashMeetsDifficulty

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
    def _sync_peer(url):
        our_blocks = get_block_list()
        blocks = requests.get(url + 'blist/0').text.splitlines()
        for block in blocks:
            if block not in our_blocks and hashMeetsDifficulty(block):
                try:
                    import_block_from_data(
                        requests.get(
                            url + f'get/{block}', stream=True).raw.read(6000000))
                except onionrexceptions.InvalidMetadata:
                    logger.warn(f"Could not get {block} from lan peer")
                except onionrexceptions.InvalidProof:
                    logger.warn(
                        f"Invalid proof for {block} from lan peer {peer}", terminal=True)
                    break

    for port in ports:
        try:
            root = f'http://{peer}:{port}/'
            if requests.get(f'{root}ping').text != 'onionr!':
                connected_lan_peers.remove(peer)
            else:
                logger.info(f'[LAN] Connected to {peer}:{port}', terminal=True)
                while True:
                    try:
                        _sync_peer(root)
                    except requests.exceptions.ConnectionError:
                        break
                break
        except requests.exceptions.ConnectionError:
            pass
    else:
        connected_lan_peers.remove(peer)


def connect_peer(peer: LANIP):
    if peer not in connected_lan_peers:
        connected_lan_peers.add(peer)
        Thread(target=_lan_work, args=[peer], daemon=True).start()

