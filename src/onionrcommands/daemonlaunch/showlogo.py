"""Onionr - Private P2P Communication.

Show nice logo
"""
import os

import config

from .quotes import QUOTE
from utils.boxprint import bordered

from utils import readstatic
import onionrvalues
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

def header():
    if onionrvalues.DEVELOPMENT_MODE:
        return

    pink_ansi = '\033[95m'
    green_ansi = '\033[92m'
    reset_ansi = '\x1b[0m'

    logo = readstatic.read_static('header.txt', ret_bin=False)
    logo = logo.replace('P', pink_ansi).replace('G', green_ansi).replace('W', reset_ansi)
    print(reset_ansi + logo)

def show_logo():
    try:
        terminal_size = os.get_terminal_size().columns
    except OSError:  # Generally thrown if not in terminal
        terminal_size = 120
    # print nice header thing :)
    if config.get('general.display_header', True):
        header()
        if terminal_size >= 120:
            if QUOTE[1]:  # If there is an author to show for the quote
                print("\u001b[33m\033[F" + bordered(QUOTE[0] + '\n -' + QUOTE[1]))
            else:
                print("\u001b[33m\033[F" + bordered(QUOTE[0]))
        else:
            if QUOTE[1]:
                print("\u001b[33m\033[F" + QUOTE[0] + '\n -' + QUOTE[1])
            else:
                print("\u001b[33m\033[F" + QUOTE[0])

