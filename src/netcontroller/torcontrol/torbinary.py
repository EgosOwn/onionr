"""Onionr - Private P2P Communication.

get the tor binary path
"""
import os
from shutil import which
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


def tor_binary():
    """Return tor binary path or none if not exists"""
    tor_path = './tor'
    if not os.path.exists(tor_path):
        tor_path = which('tor')
    return tor_path
