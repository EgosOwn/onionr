"""Onionr - Private P2P Communication.

launch the api servers and communicator
"""
import os
import sys
import platform
import signal
from threading import Thread

from stem.connection import IncorrectPassword
import stem
import toomanyobjs
import filenuke
from deadsimplekv import DeadSimpleKV
import psutil

import config

import apiservers
import logger
from onionrplugins import onionrevents as events

from onionrutils import localcommand
from utils import identifyhome
import filepaths
from etc import onionrvalues, cleanup
from onionrcrypto import getourkeypair
from utils import hastor
import runtests
from httpapi import daemoneventsapi
from .. import version
from .getapihost import get_api_host_until_available
from utils.bettersleep import better_sleep
from .killdaemon import kill_daemon  # noqa
from .showlogo import show_logo

from setupkvvars import setup_kv
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


def _proper_shutdown():
    localcommand.local_command('shutdown')
    sys.exit(1)


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
        pid = str(os.getpid())
        main_pid = localcommand.local_command('/getpid')
        #logger.info(main_pid, terminal=True)
        if main_pid and main_pid == pid:
            logger.info(
            f"Received sigterm, shutting down gracefully. PID: {pid}", terminal=True)
            localcommand.local_command('/shutdownclean')
        else:
            logger.info(
                f"Recieved sigterm in child process or fork, exiting. PID: {pid}")
            sys.exit(0)
    signal.signal(signal.SIGTERM, _handle_sig_term)

    # Determine if Onionr is in offline mode.
    # When offline, Onionr can only use LAN and disk transport
    offline_mode = config.get('general.offline_mode', False)

    if not hastor.has_tor():
        offline_mode = True
        logger.error("Tor is not present in system path or Onionr directory",
                     terminal=True)

    # Create shared objects

    shared_state = toomanyobjs.TooMany()

    # Add DeadSimpleKV for quasi-global variables (ephemeral key-value)
    shared_state.get(DeadSimpleKV)

    # Initialize the quasi-global variables
    setup_kv(shared_state.get(DeadSimpleKV))

    shared_state.get(daemoneventsapi.DaemonEventsBP)

    Thread(target=shared_state.get(apiservers.ClientAPI).start,
           daemon=True, name='client HTTP API').start()


    # Init run time tester
    # (ensures Onionr is running right, for testing purposes)
    # Run time tests are not normally run
    shared_state.get(runtests.OnionrRunTestManager)

    shared_state.share_object()  # share the parent object to the threads

    show_logo()

    # since we randomize loopback API server hostname to protect against attacks,
    # we have to wait for it to become set
    apiHost = ''
    if not offline_mode:
        apiHost = get_api_host_until_available()



    security_level = config.get('general.security_level', 1)
    use_existing_tor = config.get('tor.use_existing_tor', False)



    _show_info_messages()
    logger.info(
        "Onionr daemon is running under " + str(os.getpid()), terminal=True)
    events.event('init', threaded=False)
    events.event('daemon_start')


    better_sleep(5)

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
                logger.info(
                    f"Detected stale run file, deleting {filepaths.lock_file}", terminal=True)
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
