"""Onionr - Private P2P Communication.

return a list of strings of the user's transport addresses for the main
Onionr protocol
"""
from gevent import time

import filepaths
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

files = []


class _GetTor:
    def __init__(self):
        self.tor_hs = None

    def get(self):
        if self.tor_hs is None:
            try:
                with open(filepaths.tor_hs_address_file, 'r') as \
                     transport_file:
                    self.tor_hs = transport_file.read().strip()
                if not self.tor_hs:
                    self.tor_hs = None
            except FileNotFoundError:
                pass
        return self.tor_hs


_tor_getter = _GetTor()


def get():
    transports = [_tor_getter.get()]
    for file in files:
        try:
            with open(file, 'r') as transport_file:
                transports.append(transport_file.read().strip())
        except FileNotFoundError:
            pass
        else:
            break
    else:
        time.sleep(1)
    return list(transports)
