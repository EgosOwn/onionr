#!/usr/bin/env python3
'''
    Onionr - Private P2P Communication

    This file initializes Onionr when ran to be a daemon or with commands

    Run with 'help' for usage.
'''
'''
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
'''

# Set the user's locale for encoding reasons
import locale 
locale.setlocale(locale.LC_ALL, '')

# Import standard libraries
import sys

# 3rd party lib imports
# Ensure that PySocks is installed
try:
    from urllib3.contrib.socks import SOCKSProxyManager
except ModuleNotFoundError:
    raise ModuleNotFoundError("You need the PySocks module (for use with socks5 proxy to use Tor)")

# Onionr imports
from etc import onionrvalues # For different Onionr related constants such as versions
import onionrsetup as setup

# Ensure we have at least the minimum python version
if sys.version_info[0] == 2 or sys.version_info[1] < onionrvalues.MIN_PY_VERSION:
    sys.stderr.write('Error, Onionr requires Python 3.%s+\n' % (onionrvalues.MIN_PY_VERSION,))
    sys.exit(1)

# Create Onionr data directories, must be done before most imports
from utils import createdirs
createdirs.create_dirs()

from onionrcommands import parser
from onionrplugins import onionrevents as events

setup.setup_config()
setup.setup_default_plugins()

def onionr_main():
    parser.register()
    return

if __name__ == "__main__":
    onionr_main()

    try:
        sys.stderr.close()
    except (IOError, BrokenPipeError) as e:
        pass
    try:
        sys.stdout.close()
    except (IOError, BrokenPipeError) as e:
        pass
