"""
    Onionr - Private P2P Communication

    Keeps track of how much disk space we're using
"""
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
import config, filepaths
config.reload()
class StorageCounter:
    def __init__(self):
        self.data_file = filepaths.usage_file
        return

    def is_full(self)->bool:
        """Returns if the allocated disk space is full (this is Onionr config, not true FS capacity)"""
        ret_data = False
        if config.get('allocations.disk', 2000000000) <= (self.get_amount() + 1000):
            ret_data = True
        return ret_data

    def _update(self, data):
        with open(self.data_file, 'w') as data_file:
            data_file.write(str(data))

    def get_amount(self)->int:
        """Return how much disk space we're using (according to record)"""
        ret_data = 0
        try:
            with open(self.data_file, 'r') as data_file:
                ret_data = int(data_file.read())
        except FileNotFoundError:
            pass
        except ValueError:
            pass # Possibly happens when the file is empty
        return ret_data
    
    def get_percent(self)->int:
        """Return percent (decimal/float) of disk space we're using"""
        amount = self.get_amount()
        return round(amount / config.get('allocations.disk', 2000000000), 2)

    def add_bytes(self, amount)->int:
        """Record that we are now using more disk space, unless doing so would exceed configured max"""
        new_amount = amount + self.get_amount()
        ret_data = new_amount
        if new_amount > config.get('allocations.disk', 2000000000):
            ret_data = False
        else:
            self._update(new_amount)
        return ret_data

    def remove_bytes(self, amount)->int:
        """Record that we are now using less disk space"""
        new_amount = self.get_amount() - amount
        self._update(new_amount)
        return new_amount
