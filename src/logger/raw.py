"""Onionr - Private P2P Communication.

Output raw data to file or terminal
"""
import sys
import os
from . import settings, colors
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
colors = colors.Colors


def raw(data, fd = sys.stdout, terminal = False):
    """
        Outputs raw data to console without formatting
    """

    if terminal and (settings.get_settings() & settings.OUTPUT_TO_CONSOLE):
        try:
            ts = fd.write('%s\n' % data)
        except OSError:
            pass
    if settings.get_settings() & settings.OUTPUT_TO_FILE:
        fdata = ''
        try:
            for _ in range(5):
                try:
                    with open(settings._outputfile, 'r') as file:
                        fdata = file.read()
                except UnicodeDecodeError:
                    pass
                else:
                    break
        except FileNotFoundError:
            pass
        fdata = fdata + '\n' + data
        fdata = fdata.split('\n')
        if len(fdata) >= settings.MAX_LOG_FILE_LINES:
            fdata.pop(0)
        fdata = '\n'.join(fdata)
        with open(settings._outputfile, 'w') as file:
            file.write(fdata)
