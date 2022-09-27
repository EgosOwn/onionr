from typing import TYPE_CHECKING
from typing import List
import secrets
from asyncio import wait_for

from onionrblocks import Block

from logger import log as logging
from ..dandelion import StemAcceptResult
from ..constants import BLOCK_ID_SIZE, BLOCK_SIZE_LEN, BLOCK_MAX_SIZE
from ..constants import MAX_INBOUND_DANDELION_EDGE, MAX_STEM_BLOCKS_PER_STREAM
from ..blockqueues import gossip_block_queues


base_wait_timeout = 120

if TYPE_CHECKING:
    from asyncio import StreamWriter, StreamReader


async def accept_stem_blocks(
        reader: 'StreamReader',
        writer: 'StreamWriter',
        inbound_edge_count: List[int]):

    if inbound_edge_count[0] >= MAX_INBOUND_DANDELION_EDGE:
        writer.write(StemAcceptResult.DENY)
        return
    writer.write(StemAcceptResult.ALLOW)
    await writer.drain()
    inbound_edge_count[0] += 1


    block_queue_to_use = secrets.choice(gossip_block_queues)

    for _ in range(MAX_STEM_BLOCKS_PER_STREAM):
        read_routine = reader.readexactly(BLOCK_ID_SIZE)
        #logging.debug(f"Reading block id in stem server")
        block_id = await wait_for(read_routine, base_wait_timeout)
        block_id = block_id.decode('utf-8')
        if not block_id:
            break

        #logging.debug(f"Reading block size in stem server")
        block_size = (await wait_for(
            reader.readexactly(BLOCK_SIZE_LEN),
            base_wait_timeout)).decode('utf-8')
        if not block_size:
            break

        if not all(c in "0123456789" for c in block_size):
            raise ValueError("Invalid block size data (non 0-9 char)")
        block_size = int(block_size)
        if block_size > BLOCK_MAX_SIZE:
            raise ValueError("Max block size")

        #logging.debug(f"Reading block of size {block_size} in stem server")

        raw_block: bytes = await wait_for(
            reader.readexactly(block_size), base_wait_timeout * 6)
        if not raw_block:
            break

        logging.debug("Got a stem block, put into queue")
        block_queue_to_use.put(
            Block(block_id, raw_block, auto_verify=True)
        )

        # Regardless of stem phase, we add to queue
        # Client will decide if they are to be stemmed

