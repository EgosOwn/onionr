"""Onionr - Private P2P Communication.

read-eval-print-loop plugin for Onionr
"""

import locale


locale.setlocale(locale.LC_ALL, '')

import sys
import os
import readline
import rlcompleter
readline.parse_and_bind("tab: complete")

# locals for the repl
from gossip.peerset import gossip_peer_set

from code import InteractiveConsole
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# import after path insert

import logger

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


plugin_name = 'repl'
PLUGIN_VERSION = '0.0.0'

def on_primary_loop(event_name, data):
    """Run a REPL on the primary loop"""
    logger.disable_console_logging()
    header = """You are now in the Onionr REPL. Type 'exit()' to exit.

Enter repl_locals to see the (default) special locals available to you.
"""
    footer = "Exiting Onionr REPL."
    repl_locals = {
        'gossip_peer_set': gossip_peer_set,
    }

    InteractiveConsole(
        repl_locals | {"repl_locals": repl_locals}).interact(header, footer)
    raise KeyboardInterrupt

