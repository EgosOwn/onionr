"""Onionr - P2P Anonymous Storage Network.

Send Tor restart command
"""
from gevent import spawn

from onionrutils import localcommand
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


def rebuild():
    """Send Tor restart command"""
    spawn(
        localcommand.local_command,
        f'/daemon-event/restart_tor',
        post=True,
        is_json=True,
        post_data={}
    ).get(10)


rebuild.onionr_help = "If Onionr is running and is managing its own Tor daemon, restart that daemon."
