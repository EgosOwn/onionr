"""Onionr - Private P2P Communication.

Gracefully stop Onionr daemon
"""
import os
from signal import SIGTERM

from filepaths import pid_file
from logger import log as logging
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


def kill_daemon():
    """Shutdown the Onionr daemon (communicator)."""
    try:
        with open(pid_file, 'r') as pid:
            os.kill(int(pid.read()), SIGTERM)
    except FileNotFoundError:
        logging.error("Daemon not running/pid file missing")
    logging.warn('Stopping the running daemon, if one exists...', timestamp=False,
                )


kill_daemon.onionr_help = "Gracefully stops the "  # type: ignore
kill_daemon.onionr_help += "Onionr API servers"  # type: ignore