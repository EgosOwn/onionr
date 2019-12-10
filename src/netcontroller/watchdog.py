"""
    Onionr - Private P2P Communication

    Watch 1 process, then terminate second safely
"""

import time
import os

import psutil

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


def watchdog(parent_proc, child_proc):
    """watch for proc1 to die, then kill proc2"""

    try:
        if os.forkpty() != 0:
            return
    except AttributeError:
        pass

    parent_proc = psutil.Process(parent_proc)
    child_proc = psutil.Process(child_proc)

    while parent_proc.is_running():
        time.sleep(10)

    if child_proc.is_running():
        child_proc.terminate()
