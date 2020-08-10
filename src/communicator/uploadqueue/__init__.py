"""Onionr - Private P2P Communication.

Class to remember blocks that need to be uploaded
and not shared on startup/shutdown
"""
import atexit
import os
from typing import TYPE_CHECKING

import deadsimplekv

import filepaths
from onionrutils import localcommand
if TYPE_CHECKING:
    from communicator import OnionrCommunicatorDaemon
    from deadsimplekv import DeadSimpleKV
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

UPLOAD_MEMORY_FILE = filepaths.upload_list


def _add_to_hidden_blocks(cache):
    for bl in cache:
        localcommand.local_command('waitforshare/' + bl, post=True)


class UploadQueue:
    """Saves and loads block upload info from json file."""

    def __init__(self, communicator: 'OnionrCommunicatorDaemon'):
        """Start the UploadQueue object, loading left over uploads into queue.

        register save shutdown function
        """
        self.communicator = communicator
        cache: deadsimplekv.DeadSimpleKV = deadsimplekv.DeadSimpleKV(
            UPLOAD_MEMORY_FILE)
        self.kv: "DeadSimpleKV" = \
            communicator.shared_state.get_by_string("DeadSimpleKV")
        self.store_obj = cache
        cache = cache.get('uploads')
        if cache is None:
            cache = []

        _add_to_hidden_blocks(cache)
        self.kv.get('blocksToUpload').extend(cache)

        atexit.register(self.save)

    def save(self):
        """Save to disk on shutdown or if called manually."""
        bl: deadsimplekv.DeadSimpleKV = self.kv.get('blocksToUpload')
        if len(bl) == 0:
            try:
                os.remove(UPLOAD_MEMORY_FILE)
            except FileNotFoundError:
                pass
        else:
            self.store_obj.put('uploads', bl)
            self.store_obj.flush()
