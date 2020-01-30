"""Onionr - Private P2P Communication.

Try to provide recommendations for invalid Onionr commands
"""
import sys
from difflib import SequenceMatcher
import logger
from . import arguments
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


def recommend(print_default: bool = True):
    """Print out a recommendation for argv cmd if one is available."""
    tried = sys.argv[1]
    args = arguments.get_arguments()
    print_message = 'Command not found:'
    for key in args.keys():
        for word in key:
            if SequenceMatcher(None, tried, word).ratio() >= 0.75:
                logger.warn(f'{print_message} "{tried}", '
                            + f'did you mean "{word}"?',
                            terminal=True)
                return
    if print_default:
        logger.error('%s "%s"' % (print_message, tried), terminal=True)
