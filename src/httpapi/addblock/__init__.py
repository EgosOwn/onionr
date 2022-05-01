"""Onionr - Private P2P Communication.

Serialized APIs
"""

from asyncio.log import logger
import secrets
from flask import Blueprint, Response, request

from onionrblocks import Block

import logger
from gossip import blockqueues
from gossip.constants import BLOCK_ID_SIZE

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
blockapi = Blueprint('blockapi', __name__)


stream_to_use = secrets.randbits(1)

# Add a block that we generated (or received from a transport like LAN/sneakernet)
@blockapi.route('/addvdfblock', methods=['POST'])
def block_serialized():
    req_data = request.data
    block_id = req_data[:BLOCK_ID_SIZE]
    block_data = req_data[BLOCK_ID_SIZE:]
    blockqueues.gossip_block_queues[stream_to_use].put(
        Block(block_id, block_data, auto_verify=False))
    logger.info("Added block" + block_id, terminal=True)
    return "ok"