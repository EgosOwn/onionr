"""Onionr - Private P2P Communication.

Command to tell daemon to do run time tests
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


def do_runtime_test():
    """Send runtime test daemon queue command."""
    spawn(
        localcommand.local_command,
        f'daemon-event/test_runtime',
        post=True,
        is_json=True,
        post_data={},
        max_wait=300
    ).get(300)


do_runtime_test.onionr_help = "If Onionr is running, "  # type: ignore
do_runtime_test.onionr_help += "run runtime tests (check logs)"  # type: ignore
