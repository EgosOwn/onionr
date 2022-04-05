"""Onionr - Private P2P Communication.

Diffuse blocks we can for inbound edge peers that ask for them

doesn't apply for blocks in the gossip queue that are awaiting
descision to fluff or stem

"""
from asyncio import IncompleteReadError, wait_for

import queue
import traceback
from typing import TYPE_CHECKING
from time import time

if TYPE_CHECKING:
    from asyncio import StreamWriter, StreamReader
    from onionrblocks import Block

from ..constants import BLOCK_MAX_SIZE, BLOCK_MAX_SIZE_LEN, BLOCK_STREAM_OFFSET_DIGITS

import logger
from blockdb import get_blocks_after_timestamp, block_storage_observers
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


async def diffuse_blocks(reader: 'StreamReader', writer: 'StreamWriter'):
    """stream blocks to a peer created since an offset
    """
    time_offset = await wait_for(reader.readexactly(BLOCK_STREAM_OFFSET_DIGITS), 12)
    time_offset = time_offset.decode('utf-8')
    keep_writing = True

    # Makes sure timestamp is positive and not weird
    if not all(c in "0123456789" for c in time_offset):
        raise ValueError("Invalid time offset")
    time_offset = int(time_offset)

    if time_offset - time() > -5:
        raise ValueError(
            "Peer's specified time offset skewed too far into the future")

    newly_stored_blocks = queue.Queue()

    def _add_to_queue(bl):
        newly_stored_blocks.put_nowait(bl)
    block_storage_observers.append(
        _add_to_queue
    )

    async def _send_block(bl: 'Block'):
        writer.write(block.id)
        await writer.drain()

        # we tell id above, they tell if they want the block
        if int.from_bytes(await reader.readexactly(1), 'big') == 0:
            return

        await writer.drain()
        writer.write(
            str(len(block.raw)).zfill(BLOCK_MAX_SIZE_LEN).encode('utf-8'))
        await writer.drain()
        writer.write(block.raw)
        await writer.drain()

    try:
        # Send initial blocks from offset
        for block in get_blocks_after_timestamp(time_offset):
            if not keep_writing:
                break

            await _send_block(block)

            try:
                keep_writing = bool(
                    int.from_bytes(await reader.readexactly(1), 'big')
                )
            except IncompleteReadError:
                keep_writing = False

        # Diffuse blocks stored since we started this stream
        while keep_writing:
            await _send_block(newly_stored_blocks.get())
            try:
                keep_writing = bool(
                    int.from_bytes(await reader.readexactly(1), 'big')
                )
            except IncompleteReadError:
                keep_writing = False
    except Exception:
        logger.warn(traceback.format_exc(), terminal=True)

    block_storage_observers.remove(_add_to_queue)
