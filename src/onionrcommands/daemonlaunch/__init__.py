"""Onionr - Private P2P Communication.

launch the api servers and communicator
"""
import os
from time import sleep
import sys
import platform
import signal
from threading import Thread

import filenuke
import psutil

import config

import logger
from onionrplugins import onionrevents as events

from utils import identifyhome
import filepaths
import onionrvalues
from onionrutils import cleanup
from onionrcrypto import getourkeypair
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


def _show_info_messages():
    version.version(verbosity=5, function=logger.info)
    logger.debug('Python version %s' % platform.python_version())

    if onionrvalues.DEVELOPMENT_MODE:
        logger.warn('Development mode enabled', timestamp=False, terminal=True)

    logger.info('Using public key: %s' %
                (logger.colors.underline +
                 getourkeypair.get_keypair()[0][:52]))


def daemon():
    """Start Onionr's primary threads for communicator, API server, node, and LAN."""

    def _handle_sig_term(signum, frame):
        sys.exit(0)

    with open(filepaths.pid_file, 'w') as f:
        f.write(str(os.getpid()))

    signal.signal(signal.SIGTERM, _handle_sig_term)


    show_logo()

    security_level = config.get('general.security_level', 1)

    _show_info_messages()
    logger.info(
        f"Onionr daemon is running under pid {os.getpid()}", terminal=True)
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
            sleep(60)
    except KeyboardInterrupt:
        pass

    cleanup.delete_run_files()
    if security_level >= 2:
        filenuke.nuke.clean_tree(identifyhome.identify_home())


def start(override: bool = False):
    """If no lock file, make one and start onionr.

    Error exit if there is and its not overridden
    """
    if os.path.exists(filepaths.lock_file) and not override:
        if os.path.exists(filepaths.restarting_indicator):
            try:
                os.remove(filepaths.restarting_indicator)
            except FileNotFoundError:
                pass
            else:
                return
        with open(filepaths.lock_file, 'r') as lock_file:
            try:
                proc = psutil.Process(int(lock_file.read())).name()
            except psutil.NoSuchProcess:
                proc = ""
            if not proc.startswith("python"):
                logger.warn(
                    f"Detected stale run file, deleting {filepaths.lock_file}",
                    terminal=True)
                try:
                    os.remove(filepaths.lock_file)
                except FileNotFoundError:
                    pass
                start(override=True)
                return
        logger.fatal('Cannot start. Daemon is already running,'
                     + ' or it did not exit cleanly.\n'
                     + ' (if you are sure that there is not a daemon running,'
                     + f' delete {filepaths.lock_file} & try again).',
                     terminal=True)
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
