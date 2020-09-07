"""Onionr - Private P2P Communication.

Show nice logo
"""
import os

import config
import logger

from .quotes import QUOTE
from utils.boxprint import bordered
from utils import logoheader
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


def show_logo():
    logger.raw('', terminal=True)
    try:
        terminal_size = os.get_terminal_size().columns
    except OSError:  # Generally thrown if not in terminal
        terminal_size = 120
    # print nice header thing :)
    if config.get('general.display_header', True):
        logoheader.header("")
        if terminal_size >= 120:
            if QUOTE[1]:  # If there is an author to show for the quote
                logger.info(
                    "\u001b[33m\033[F" + bordered(QUOTE[0] + '\n -' + QUOTE[1]),
                    terminal=True)
            else:
                logger.info(
                    "\u001b[33m\033[F" + bordered(QUOTE[0]), terminal=True)
        else:
            if QUOTE[1]:
                logger.info("\u001b[33m\033[F" + QUOTE[0] + '\n -' + QUOTE[1],
                            terminal=True)
            else:
                logger.info("\u001b[33m\033[F" + QUOTE[0], terminal=True)

