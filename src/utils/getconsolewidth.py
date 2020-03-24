"""Onionr - Private P2P Communication.

Get the width of the terminal screen
"""
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


def get_console_width() -> int:
    """Return the width of the terminal/cmd window."""

    columns = 80

    try:
        columns = int(os.popen('stty size', 'r').read().split()[1])
    except:
        # if it errors, it's probably windows, so default to 80.
        pass

    return columns
