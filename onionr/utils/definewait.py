'''
    Onionr - Private P2P Communication

    Waits for a key to become set in a dictionary, even to None, 0 or empty string
'''
'''
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
'''
import time
def define_wait(dictionary, key, delay: int = 0):
    while True:
        try:
            return dictionary[key]
        except KeyError:
            pass
        if delay > 0:
            time.sleep(delay)