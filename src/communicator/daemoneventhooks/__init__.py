"""Onionr - Private P2P Communication.

Hooks to handle daemon events
"""
from threading import Thread

from .removefrominsertqueue import remove_from_insert_queue

from typing import TYPE_CHECKING

from gevent import sleep

from communicatorutils.uploadblocks import mixmate
from communicatorutils import restarttor

if TYPE_CHECKING:
    from toomanyobjs import TooMany
    from deadsimplekv import DeadSimpleKV
    from communicator import OnionrCommunicatorDaemon
    from httpapi.daemoneventsapi import DaemonEventsBP
    from onionrtypes import BlockHash
    from apiservers import PublicAPI
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


def daemon_event_handlers(shared_state: 'TooMany'):
    def _get_inst(class_name: str):
        while True:
            try:
                return shared_state.get_by_string(class_name)
            except KeyError:
                sleep(0.2)
    comm_inst = _get_inst('OnionrCommunicatorDaemon')
    public_api: 'PublicAPI' = _get_inst('PublicAPI')
    events_api: 'DaemonEventsBP' = _get_inst('DaemonEventsBP')
    kv: 'DeadSimpleKV' = _get_inst('DeadSimpleKV')

    def remove_from_insert_queue_wrapper(block_hash: 'BlockHash'):
        remove_from_insert_queue(comm_inst, block_hash)
        return "removed"

    def print_test(text=''):
        print("It works!", text)
        return f"It works! {text}"

    def upload_event(block: 'BlockHash' = ''):
        if not block:
            raise ValueError
        public_api.hideBlocks.append(block)
        try:
            mixmate.block_mixer(kv.get('blocksToUpload'), block)
        except ValueError:
            pass
        return "removed"

    def restart_tor():
        restarttor.restart(shared_state)
        kv.put('offlinePeers', [])
        kv.put('onlinePeers', [])

    def test_runtime():
        Thread(target=comm_inst.shared_state.get_by_string(
            "OnionrRunTestManager").run_tests).start()

    events_api.register_listener(remove_from_insert_queue_wrapper)
    events_api.register_listener(restart_tor)
    events_api.register_listener(print_test)
    events_api.register_listener(upload_event)
    events_api.register_listener(test_runtime)
