from typing import TYPE_CHECKING
from typing import List, Tuple
import secrets
from time import time
from asyncio import wait_for

from onionrblocks import Block

from ..dandelion import DandelionPhase, StemAcceptResult
from ..constants import BLOCK_ID_SIZE, BLOCK_MAX_SIZE
from ..constants import MAX_INBOUND_DANDELION_EDGE, MAX_STEM_BLOCKS_PER_STREAM


block_size_digits = len(str(BLOCK_MAX_SIZE))
base_wait_timeout = 10

if TYPE_CHECKING:
    from queue import Queue
    from asyncio import StreamWriter, StreamReader


async def accept_stem_blocks(
        block_queues: Tuple[Queue['Block'], Queue['Block']],
        reader: 'StreamReader',
        writer: 'StreamWriter',
        inbound_edge_count: List[int]):

    if inbound_edge_count[0] >= MAX_INBOUND_DANDELION_EDGE:
        writer.write(StemAcceptResult.DENY)
        return
    writer.write(StemAcceptResult.ALLOW)
    inbound_edge_count[0] += 1

    # Start getting the first block
    read_routine = reader.read(BLOCK_ID_SIZE)
    stream_start_time = int(time())

    block_queue_to_use = secrets.choice(block_queues)

    for _ in range(MAX_STEM_BLOCKS_PER_STREAM):
        block_id = (
            await wait_for(read_routine, base_wait_timeout)).decode('utf-8')
        block_size = (await wait_for(
            reader.read(block_size_digits),
            base_wait_timeout)).decode('utf-8')

        if not all(c in "0123456789" for c in block_size):
            raise ValueError("Invalid block size data (non 0-9 char)")
        block_size = int(block_size)
        if block_size > BLOCK_MAX_SIZE:
            raise ValueError("Max block size")

        raw_block: bytes = await wait_for(
            reader.read(block_size), base_wait_timeout * 6)

        block_queue_to_use.put(
            Block(block_id, raw_block, auto_verify=True)
        )
        # Regardless of stem phase, we add to queue
        # Client will decide if they are to be stemmed

        read_routine = reader.read(BLOCK_ID_SIZE)
