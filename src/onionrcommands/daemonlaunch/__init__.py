"""Onionr - Private P2P Communication.

launch the api servers and communicator
"""
import os
from time import sleep
import sys
import platform
import signal
from threading import Thread
from logger import log as logging
from logger import enable_file_logging

import filenuke
import psutil

import config

from onionrplugins import onionrevents as events

from utils import identifyhome
import filepaths
import onionrvalues
from onionrthreads import add_onionr_thread
from blockdb.blockcleaner import clean_block_database
from .. import version
from .killdaemon import kill_daemon  # noqa
from .showlogo import show_logo
import gossip

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

def _safe_remove(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def delete_run_files():
    """Delete run files, do not error if not found.

    Test: test_cleanup.py
    """
    _safe_remove(filepaths.lock_file)
    _safe_remove(filepaths.gossip_server_socket_file)
    _safe_remove(filepaths.pid_file)

def _show_info_messages():
    version.version(verbosity=5, function=logging.info)
    logging.debug('Python version %s' % platform.python_version())

    if onionrvalues.DEVELOPMENT_MODE:
        logging.warn('Development mode enabled')


def daemon():
    """Start Onionr's primary threads for communicator, API server, node, and LAN."""

    if config.get('log.file.output', False):
        enable_file_logging()

    def _handle_sig_term(signum, frame):
        sys.exit(0)

    with open(filepaths.pid_file, 'w') as f:
        f.write(str(os.getpid()))

    signal.signal(signal.SIGTERM, _handle_sig_term)


    show_logo()

    security_level = config.get('general.security_level', 1)

    _show_info_messages()
    logging.info(
        f"Onionr daemon is running under pid {os.getpid()}")
    events.event('init', threaded=False)
    events.event('afterinit', threaded=False)
    events.event('daemon_start')

    add_onionr_thread(
        clean_block_database, 60, 'clean_block_database', initial_sleep=0)

    Thread(
        target=gossip.start_gossip_threads,
        daemon=True,
        name='start_gossip_threads').start()

    try:
        while True:
            # Mainly for things like repls
            events.event('primary_loop', threaded=False)
            sleep(60)
    except KeyboardInterrupt:
        pass


    delete_run_files()
    if security_level >= 2:
        filenuke.nuke.clean_tree(identifyhome.identify_home())


def start(override: bool = False):
    """If no lock file, make one and start onionr.

    Error exit if there is and its not overridden
    """
    if os.path.exists(filepaths.lock_file) and not override:
        with open(filepaths.lock_file, 'r') as lock_file:
            try:
                proc = psutil.Process(int(lock_file.read())).name()
            except psutil.NoSuchProcess:
                proc = ""
            if not proc.startswith("python"):
                logging.warn(
                    f"Detected stale run file, deleting {filepaths.lock_file}")
                try:
                    os.remove(filepaths.lock_file)
                except FileNotFoundError:
                    pass
                start(override=True)
                return
        logging.error('Cannot start. Daemon is already running,'
                     + ' or it did not exit cleanly.\n'
                     + ' (if you are sure that there is not a daemon running,'
                     + f' delete {filepaths.lock_file} & try again).',
                     )
    else:
        if not onionrvalues.DEVELOPMENT_MODE:
            lock_file = open(filepaths.lock_file, 'w')
            lock_file.write(str(os.getpid()))
            lock_file.close()

        # Start Onionr daemon
        daemon()

        try:
            os.remove(filepaths.lock_file)
        except FileNotFoundError:
            pass


start.onionr_help = "Start Onionr node "  # type: ignore
start.onionr_help += "(public and clients API servers)"  # type: ignore
