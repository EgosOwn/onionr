"""Onionr - Private P2P Communication.

Command to show version info
"""
import platform
from utils import identifyhome
import onionrvalues
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


def version(verbosity=5, function=logging.info):
    """Display the Onionr version."""
    function('Onionr v%s (%s)' % (onionrvalues.ONIONR_VERSION,
                                            platform.machine()))
    if verbosity >= 1:
        function(onionrvalues.ONIONR_TAGLINE)
    if verbosity >= 2:
        pf = platform.platform()
        release = platform.release()
        python_imp = platform.python_implementation()
        python_version = platform.python_version()
        function(
            f'{python_imp} {python_version} on {pf} {release}')
        function('Onionr data dir: %s' %
                 identifyhome.identify_home())


version.onionr_help = 'Shows environment details including '  # type: ignore
version.onionr_help += 'Onionr version & data directory, '  # type: ignore
version.onionr_help += 'OS and Python version'  # type: ignore
