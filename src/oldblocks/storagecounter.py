"""
Onionr - Private P2P Communication.

Keep track of how much disk space we're using
"""
from pathlib import Path

from threading import Thread

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config
from filepaths import usage_file
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
config.reload()


def _read_data_file(f) -> int:
    amount = 0
    try:
        with open(f, 'r') as f:
            amount = int(f.read())
    except FileNotFoundError:
        pass
    except ValueError:
        pass  # Possibly happens when the file is empty
    return amount


class StorageCounter:
    def __init__(self):
        self.data_file = usage_file
        self.amount: int = None
        Path(self.data_file).touch()

        def auto_refresher():
            class Refresher(FileSystemEventHandler):
                @staticmethod
                def on_modified(event):
                    self.amount = _read_data_file(self.data_file)
            observer = Observer()
            observer.schedule(Refresher(), usage_file)
            observer.start()
            while observer.is_alive():
                # call import func with timeout
                observer.join(120)
        Thread(target=auto_refresher, daemon=True).start()
        self.amount = _read_data_file(self.data_file)

    def is_full(self) -> bool:
        """Returns if the allocated disk space is full (this is Onionr config,
        not true FS capacity)"""
        ret_data = False
        if config.get('allocations.disk', 1073741824) <= (self.amount + 1000):
            ret_data = True
        return ret_data

    def _update(self, data):
        with open(self.data_file, 'w') as data_file:
            data_file.write(str(data))

    def get_percent(self) -> int:
        """Return percent (decimal/float) of disk space we're using"""
        amount = self.amount
        return round(amount / config.get('allocations.disk', 2000000000), 2)

    def add_bytes(self, amount) -> int:
        """Record that we are now using more disk space,
        unless doing so would exceed configured max"""
        new_amount = amount + self.amount
        ret_data = new_amount
        if new_amount > config.get('allocations.disk', 2000000000):
            ret_data = False
        else:
            self._update(new_amount)
        return ret_data

    def remove_bytes(self, amount) -> int:
        """Record that we are now using less disk space"""
        new_amount = self.amount - amount
        self._update(new_amount)
        return new_amount
