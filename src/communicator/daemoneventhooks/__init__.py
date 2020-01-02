"""Onionr - Private P2P Communication.

Hooks to handle daemon events
"""
from typing import TYPE_CHECKING

from gevent import sleep

if TYPE_CHECKING:
    from toomanyobjs import TooMany
    from communicator import OnionrCommunicatorDaemon
    from httpapi.daemoneventsapi import DaemonEventsBP
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
    events_api: 'DaemonEventsBP' = _get_inst('DaemonEventsBP')
    

