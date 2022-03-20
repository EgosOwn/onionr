from typing import TYPE_CHECKING

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

    with peer_socket:
        while remaining_time > 5 and my_phase_id == d_phase.phase_id:
            # Primary client component that communicate's with gossip.server.acceptstem
            remaining_time = d_phase.remaining_time()
            bl: 'Block' = block_queue.get(block=True, timeout=remaining_time)
            peer_socket.sendall(bl.id)
            peer_socket.sendall(len(bl.raw))
            peer_socket.sendall(bl.raw)
