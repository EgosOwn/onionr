#!/usr/bin/env python3
"""Onionr - Private P2P Communication.

This file initializes Onionr when ran to be a daemon or with commands

Run with 'help' for usage.
"""
# Enable pyjion if we can because why not
pyjion_enabled = False
try:
    pass
    #import pyjion
    #pyjion.enable()
    #pyjion_enabled = True
except ImportError:
    pass


import os
import cProfile
import threading

onionr_profiling = os.getenv("ONIONR_PROFILING", False)


import sys

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
import locale  # noqa
locale.setlocale(locale.LC_ALL, '')  # noqa

import traceback
import signal

def sigusr_stacktrace(signum, frame):
    """Print stacktrace on SIGUSR1"""
    stack_trace_file = os.getenv('ONIONR_STACK_TRACE_FILE', False)
    for th in threading.enumerate():
        if stack_trace_file:
            with open(stack_trace_file, 'a') as f:
                f.write(f'Thread: {th.name}')
                f.write('-' * 44 + '')
                traceback.print_stack(sys._current_frames()[th.ident], file=f)
        else:
            print(f'Thread: {th.name}')
            print('-' * 44)
            traceback.print_stack(sys._current_frames()[th.ident])
    #print(traceback.format_stack(frame))

signal.signal(signal.SIGUSR1, sigusr_stacktrace)


ran_as_script = False
if __name__ == "__main__": ran_as_script = True

# Import 3rd party libraries

from filenuke import nuke  # noqa

# Onionr imports

# For different Onionr related constants such as versions
import onionrvalues  # noqa

import onionrexceptions  # noqa
import onionrsetup as setup  # noqa
setup.setup_config()

setup.setup_default_plugins()

min_ver = onionrvalues.MIN_PY_VERSION

# Ensure we have at least the minimum python version
if sys.version_info[0] == 2 or sys.version_info[1] < min_ver:
    sys.stderr.write(
        'Error, Onionr requires Python 3.' + str(min_ver) + '\n')
    sys.exit(1)

# Create Onionr data directories, must be done before most imports
from utils import createdirs
createdirs.create_dirs()

import bigbrother  # noqa
from onionrcommands import parser  # noqa
from onionrplugins import onionrevents as events  # noqa



import config  # noqa
from utils import identifyhome  # noqa
import filepaths  # noqa

if config.get('advanced.security_auditing', True) \
        and not onionr_profiling:
    try:
        bigbrother.enable_ministries()
    except onionrexceptions.PythonVersion:
        pass


def onionr_main():
    """Onionr entrypoint, start command processor

    Entrypoint for daemon is commands/daemonlaunch/__init__.py
    """
    parser.register()


if ran_as_script:
    if onionr_profiling:
        cProfile.run('onionr_main()')
    else:
        onionr_main()

    config.reload()

    # If the setting is there, shred log file on exit
    if config.get('log.file.remove_on_exit', True):
        try:
            nuke.clean(filepaths.log_file)
        except FileNotFoundError:
            pass

    # Cleanup standard out/err because Python refuses to do it itsself
    try:
        sys.stderr.close()
    except (IOError, BrokenPipeError):
        pass
    try:
        sys.stdout.close()
    except (IOError, BrokenPipeError):
        pass
