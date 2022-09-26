"""Onionr - Private P2P Communication.

Processes interpreter hook events to detect security leaks
"""
import sys
import os
from typing import Iterable

import logger

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
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import ministry

plugin_name = 'bigbrother'
PLUGIN_VERSION = '0.0.0'

def sys_hook_entrypoint(event, info):
    """Entrypoint for big brother sys auditors."""
    if event == 'socket.connect':
        ministry.ofcommunication.detect_socket_leaks(info)
    elif event == 'exec':
        # logs and block both exec and eval
        ministry.ofexec.block_exec(event, info)
    elif event == 'system':
        ministry.ofexec.block_system(info)
    elif event == 'open':
        ministry.ofdisk.detect_disk_access(info)


def enable_ministries(disable_hooks: Iterable = None):
    """Enable auditors."""
    disable_hooks = disable_hooks or []
    sys.addaudithook(sys_hook_entrypoint)


def on_init(api, data=None):
    enable_ministries()
    logger.info(
        "Big brother enabled, blocking unsafe Python code.", terminal=True)
