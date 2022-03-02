from typing import TYPE_CHECKING
from typing import List
from queue import Queue
from time import time
from asyncio import wait_for

from ..constants import BLOCK_ID_SIZE, BLOCK_MAX_SIZE


block_size_digits = len(str(BLOCK_MAX_SIZE))
base_wait_timeout = 10

if TYPE_CHECKING:
    from onionrblocks import Block
    from asyncio import StreamWriter, StreamReader


async def accept_stem_blocks(
        block_queues: List[Queue['Block']],
        reader: 'StreamReader',
        writer: 'StreamWriter'):

    # Start getting the first block
    read_routine = reader.read(BLOCK_ID_SIZE)
    stream_start_time = int(time())
    max_accept_blocks = 1000

    q = Queue()
    block_queues.append(q)

    for _ in range(max_accept_blocks):
        block_id = await wait_for(read_routine, base_wait_timeout)
        block_size = int(
            await wait_for(
                reader.read(block_size_digits),
                base_wait_timeout)).decode('utf-8')


        if not all(c in "0123456789" for c in block_size):
            raise ValueError("Invalid block size data (non 0-9 char)")
        if block_size > BLOCK_MAX_SIZE:
            raise ValueError("Max block size")
        


    


