"""Onionr - Private P2P Communication.

Detect new block files in a given directory
"""
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config
from filepaths import block_data_location
from etc.onionrvalues import BLOCK_EXPORT_FILE_EXT
from onionrblocks.blockimporter import import_block_from_data
import onionrexceptions
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

watch_paths = config.get('transports.sneakernet.paths', list([]))
if block_data_location not in watch_paths:
    watch_paths.append(block_data_location)


class _Importer(FileSystemEventHandler):
    @staticmethod
    def on_created(event):
        if not event.src_path.endswith(BLOCK_EXPORT_FILE_EXT):
            return
        try:
            with open(event.src_path, 'rb') as block_file:
                block_data = block_file.read()
        except FileNotFoundError:
            return
        os.remove(event.src_path)
        try:
            import_block_from_data(block_data)
        except(  # noqa
                onionrexceptions.DataExists,
                onionrexceptions.BlockMetaEntryExists,
                onionrexceptions.InvalidMetadata) as _:
            return
        if block_data_location in event.src_path:
            try:
                os.remove(event.src_path)
            except FileNotFoundError:
                pass


def sneakernet_import_thread():
    """Add block data dir & confed paths to fs observer to watch for new bls"""
    observer = Observer()
    for path in watch_paths:
        observer.schedule(_Importer(), path, recursive=True)
    observer.start()
    while observer.is_alive():
        # call import func with timeout
        observer.join(60)
