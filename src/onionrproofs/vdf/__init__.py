"""Onionr - Private P2P Communication.

verifiable delay function proof
"""
from multiprocessing import Process
from multiprocessing import Pipe

from mimcvdf import vdf_create
from mimcvdf import vdf_verify
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.c

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
ROUND_MULTIPLIER_PER_BYTE = 100


def create(data: bytes) -> str:
    rounds = len(data) * ROUND_MULTIPLIER_PER_BYTE
    return vdf_create(data, rounds)


def multiproces_create(data: bytes) -> str:
    parent_conn, child_conn = Pipe()
    def __do_create(conn, data):
        conn.send(create(data))
        conn.close()
    p = Process(target=__do_create, args=(child_conn, data))
    p.start()
    return parent_conn.recv()


def verify(data: bytes, block_id: str) -> bool:
    rounds = len(data) * ROUND_MULTIPLIER_PER_BYTE
    return vdf_verify(data, block_id, rounds)

