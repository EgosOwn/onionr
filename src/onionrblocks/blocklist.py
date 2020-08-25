"""Onionr - Private P2P Communication.

Get an auto updating list of blocks
"""
from threading import Thread

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from utils.identifyhome import identify_home
from coredb.dbfiles import block_meta_db
from coredb.blockmetadb import get_block_list, get_blocks_by_type
from onionrutils.epoch import get_epoch
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

class BlockList:
    def __init__(self, auto_refresh=True, block_type=''):
        self.block_type = block_type
        self.refresh_db()
        self.check_time = get_epoch()

        class Refresher(FileSystemEventHandler):
            @staticmethod
            def on_modified(event):
                if event.src_path != block_meta_db:
                    return
                self.refresh_db()
        if auto_refresh:
            def auto_refresher():
                observer = Observer()
                observer.schedule(
                    Refresher(), identify_home(), recursive=False)
                observer.start()
                while observer.is_alive():
                    # call import func with timeout
                    observer.join(120)
            Thread(target=auto_refresher, daemon=True).start()

    def get(self):
        return self.block_list

    def refresh_db(self):
        self.check_time = get_epoch()
        if not self.block_type:
            self.block_list = get_block_list()
        else:
            self.block_list = get_blocks_by_type(self.block_type)
