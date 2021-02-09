from typing import TYPE_CHECKING
import sys
import os

import logger
from blockio import store_block, subprocvalidate
import onionrblocks
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from commands import GossipCommands

if TYPE_CHECKING:
    from socket import socket


def download_blocks(sock: 'socket', offset: int, block_type: str):
    sock.sendall(
        int(GossipCommands.LIST_BLOCKS_BY_TYPE_OFFSET).to_bytes(
            1, 'little') + str(offset).encode('utf-8') +
            block_type.encode('utf-8'))
    bl_hashs = sock.recv(600000)
    hash = None
    for i in range(len(bl_hashs)//64):
        hash = bl[:(i*64) + 64]
        sock.sendall(
            int(GossipCommands.GET_BLOCK).to_bytes(
                1, 'little') + hash)
        bl_content = sock.recv(10**6)


