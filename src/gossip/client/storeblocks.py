from typing import TYPE_CHECKING, Tuple
from threading import Thread
from queue import Queue
from queue import Empty

from onionrplugins.onionrevents import event
import blockdb

if TYPE_CHECKING:
    from onionrblocks import Block
    from ..dandelion.phase import DandelionPhase

from ..blockqueues import gossip_block_queues


def store_blocks(dandelion_phase: 'DandelionPhase'):

    new_queue: "Queue[Block]" = Queue()

    def _watch_queue(block_queue: "Queue[Block]"):
        # Copy all incoming blocks into 1 queue which gets processed to db
        while not dandelion_phase.is_stem_phase() \
                and dandelion_phase.remaining_time() > 1:
            try:
                new_queue.put(
                    block_queue.get(timeout=dandelion_phase.remaining_time()))
            except Empty:
                pass

    for block_queue in gossip_block_queues:
        Thread(target=_watch_queue, args=[block_queue], daemon=True).start()

    while not dandelion_phase.is_stem_phase() \
            and dandelion_phase.remaining_time() > 1:
        try:
            bl = new_queue.get(timeout=dandelion_phase.remaining_time() + 1)
            blockdb.add_block_to_db(bl)
            event('gotblock', data=bl, threaded=True)
        except Empty:
            pass
