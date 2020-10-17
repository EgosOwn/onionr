"""Onionr - Private P2P Communication.

get static directory and read static data files
"""
from typing import Union
import os
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


def get_static_dir() -> str:
    return os.path.dirname(os.path.realpath(__file__)) + '/../../static-data/'


def read_static(file: str, ret_bin: bool = False) -> Union[str, bytes]:
    static_file = get_static_dir() + file

    if ret_bin:
        mode = 'rb'
    else:
        mode = 'r'
    with open(static_file, mode, encoding='utf-8') as f:
        data = f.read()
    return data
