from typing import TYPE_CHECKING
import sys
import os

from kasten import Kasten
from kasten.generator import pack

import logger
from blockio import store_block, subprocvalidate, list_all_blocks
import onionrblocks
from onionrblocks.exceptions import BlockExpired
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from commands import GossipCommands

if TYPE_CHECKING:
    from socket import socket


def download_blocks(
        safe_db, sock: 'socket', offset: int, block_type: str) -> int:
    sock.sendall(
        str(int(GossipCommands.LIST_BLOCKS_BY_TYPE_OFFSET)).encode('utf-8') +
        str(offset).encode('utf-8') + b',' +
        block_type.encode('utf-8'))
    bl_hashs = sock.recv(600000)
    existing_blocks = list_all_blocks(safe_db)
    existing_blocks_hashes = b''
    downloaded_total = 0  # Including non-succesful
    for i in existing_blocks:
        for x in i:
            existing_blocks_hashes += int(x).to_bytes(1, 'little')
    print('existing', existing_blocks_hashes)
    hash = None
    for i in range(len(bl_hashs)//64):
        downloaded_total += 1
        hash = bl_hashs[:(i*64) + 64]
        if hash in existing_blocks_hashes:
            continue
        sock.sendall(
            str(int(GossipCommands.GET_BLOCK)).encode('utf-8') + hash)
        bl_content = sock.recv(10**6)
        if bl_content == b'0':
            existing_blocks.append(hash)
            continue
        print('got block', bl_content)
        try:
            store_block(
                Kasten(
                    hash,
                    bl_content,
                    generator=onionrblocks.generators.AnonVDFGenerator),
                safe_db
            )
            existing_blocks_hashes += hash
            print('stored block!')
        except BlockExpired:
            print('Block expired', hash)
            existing_blocks_hashes += hash
        except ValueError:
            #print('not storing dupe block')
            existing_blocks_hashes += hash
    return downloaded_total

