#!/usr/bin/env python3
"""
    Onionr - Private P2P Communication

    This file initializes Onionr when ran to be a daemon or with commands

    Run with 'help' for usage.
"""
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

# Set the user's locale for encoding reasons
import locale # noqa
locale.setlocale(locale.LC_ALL, '')

ran_as_script = False
if __name__ == "__main__": ran_as_script = True

# Import standard libraries
import sys # noqa

try:
    from etc import dependencycheck # noqa
except ModuleNotFoundError as e:
    print('Onionr needs ' + str(e) + ' installed')

# Onionr imports

# For different Onionr related constants such as versions
from etc import onionrvalues # noqa

import onionrexceptions # noqa
import onionrsetup as setup # noqa

min_ver = onionrvalues.MIN_PY_VERSION

# Ensure we have at least the minimum python version
if sys.version_info[0] == 2 or sys.version_info[1] < min_ver:
    sys.stderr.write('Error, Onionr requires Python 3.' + str(min_ver) + '\n')
    sys.exit(1)

# Create Onionr data directories, must be done before most imports
from utils import createdirs
createdirs.create_dirs()

import bigbrother # noqa
from onionrcommands import parser # noqa
from onionrplugins import onionrevents as events # noqa
from onionrblocks.deleteplaintext import delete_plaintext_no_blacklist  # noqa

setup.setup_config()

import config # noqa
from utils import identifyhome

if config.get('advanced.security_auditing', True):
    try:
        bigbrother.enable_ministries()
    except onionrexceptions.PythonVersion:
        pass

if not config.get('general.store_plaintext_blocks', True):
    delete_plaintext_no_blacklist()

setup.setup_default_plugins()


def onionr_main():
    """Onionr entrypoint, start command processor"""
    parser.register()


if ran_as_script:
    onionr_main()

    # Wipe Onionr data directory if security level calls for it
    config.reload()

    # Cleanup standard out/err because Python refuses to do it itsself
    try:
        sys.stderr.close()
    except (IOError, BrokenPipeError):
        pass
    try:
        sys.stdout.close()
    except (IOError, BrokenPipeError):
        pass
