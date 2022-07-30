from asyncio import sleep
from threading import Thread
from queue import Empty

from typing import TYPE_CHECKING

import logger
from ...constants import BLOCK_ID_SIZE, BLOCK_MAX_SIZE, BLOCK_SIZE_LEN

if TYPE_CHECKING:
    from queue import Queue
    import socket
    from ...dandelion import DandelionPhase

    from onionrblocks import Block


async def do_stem_stream(
        peer_socket: 'socket.socket',
        block_queue: "Queue[Block]",
        d_phase: 'DandelionPhase'):
    remaining_time = d_phase.remaining_time()
    my_phase_id = d_phase.phase_id

    
    while remaining_time > 1 and my_phase_id == d_phase.phase_id:
        # Primary client component that communicate's with gossip.server.acceptstem
        remaining_time = d_phase.remaining_time()
        while remaining_time:
            try:
                # queues can't block because we're in async
                bl = block_queue.get(block=False)
            except Empty:
                remaining_time = d_phase.remaining_time()
                await sleep(1)
            else:
                break
        logger.info("Sending block over dandelion++", terminal=True)

        block_size = str(len(bl.raw)).zfill(BLOCK_SIZE_LEN)
        def _send_it():
            try:
                with peer_socket:
                    try:
                        peer_socket.sendall(bl.id.zfill(BLOCK_ID_SIZE).encode('utf-8'))
                    except AttributeError:
                        peer_socket.sendall(bl.id.zfill(BLOCK_ID_SIZE))
                    peer_socket.sendall(block_size.encode('utf-8'))
                    peer_socket.sendall(bl.raw)
            except OSError:
                pass
        Thread(target=_send_it, daemon=True, name="stemout block").start()
