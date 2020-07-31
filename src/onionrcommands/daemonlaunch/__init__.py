"""Onionr - Private P2P Communication.

launch the api servers and communicator
"""
import os
import sys
import platform
from threading import Thread

from stem.connection import IncorrectPassword
import toomanyobjs
import filenuke
from deadsimplekv import DeadSimpleKV

import config
import onionrstatistics
from onionrstatistics import serializeddata
import apiservers
import logger
import communicator
from onionrplugins import onionrevents as events
from netcontroller import NetController
from netcontroller import clean_ephemeral_services
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
from netcontroller.torcontrol.onionservicecreator import create_onion_service
from .killdaemon import kill_daemon  # noqa
from .showlogo import show_logo
from lan import LANManager
from lan.server import LANServer
from sneakernet import sneakernet_import_thread
from onionrstatistics.devreporting import statistics_reporter
from setupkvvars import setup_kv
from .spawndaemonthreads import spawn_client_threads
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

def _setup_online_mode(use_existing_tor: bool,
                   net: NetController,
                   security_level: int):
    if config.get('transports.tor', True):
        # If we are using tor, check if we are using an existing tor instance
        # if we are, we need to create an onion service on it and set attrs on our NetController
        # if not, we need to tell netcontroller to start one
        if use_existing_tor:
            try:
                os.mkdir(filepaths.tor_hs_loc)
            except FileExistsError:
                pass
            net.socksPort = config.get('tor.existing_socks_port')
            try:
                net.myID = create_onion_service(
                    port=net.apiServerIP + ':' + str(net.hsPort))[0]
            except IncorrectPassword:
                # Exit if we cannot connect to the existing Tor instance
                logger.error('Invalid Tor control password', terminal=True)
                localcommand.local_command('shutdown')
                cleanup.delete_run_files()
                sys.exit(1)

            if not net.myID.endswith('.onion'):
                net.myID += '.onion'
            with open(filepaths.tor_hs_address_file, 'w') as tor_file:
                tor_file.write(net.myID)
        else:
            logger.info('Tor is starting...', terminal=True)
            if not net.startTor():
                # Exit if we cannot start Tor.
                localcommand.local_command('shutdown')
                cleanup.delete_run_files()
                sys.exit(1)
        if len(net.myID) > 0 and security_level == 0:
            logger.debug('Started .onion service: %s' %
                        (logger.colors.underline + net.myID))
        else:
            logger.debug('.onion service disabled')


def daemon():
    """Start Onionr's primary threads for communicator, API server, node, and LAN."""
    # Determine if Onionr is in offline mode.
    # When offline, Onionr can only use LAN and disk transport
    offline_mode = config.get('general.offline_mode', False)

    if not hastor.has_tor():
        offline_mode = True
        logger.error("Tor is not present in system path or Onionr directory",
                     terminal=True)

    # remove runcheck if it exists
    if os.path.isfile(filepaths.run_check_file):
        logger.debug('Runcheck file found on daemon start, deleting.')
        os.remove(filepaths.run_check_file)

    # Create shared objects

    shared_state = toomanyobjs.TooMany()

    # Add DeadSimpleKV for quasi-global variables (ephemeral key-value)
    shared_state.get(DeadSimpleKV)

    # Initialize the quasi-global variables
    setup_kv(shared_state.get(DeadSimpleKV))

    spawn_client_threads(shared_state)
    shared_state.get(daemoneventsapi.DaemonEventsBP)

    Thread(target=shared_state.get(apiservers.ClientAPI).start,
           daemon=True, name='client HTTP API').start()
    if not offline_mode:
        Thread(target=shared_state.get(apiservers.PublicAPI).start,
               daemon=True, name='public HTTP API').start()

    # Init run time tester
    # (ensures Onionr is running right, for testing purposes)
    # Run time tests are not normally run
    shared_state.get(runtests.OnionrRunTestManager)

    # Create singleton
    shared_state.get(serializeddata.SerializedData)

    shared_state.share_object()  # share the parent object to the threads

    show_logo()

    # since we randomize loopback API server hostname to protect against attacks,
    # we have to wait for it to become set
    apiHost = ''
    if not offline_mode:
        apiHost = get_api_host_until_available()

    net = NetController(config.get('client.public.port', 59497),
                        apiServerIP=apiHost)
    shared_state.add(net)

    shared_state.get(onionrstatistics.tor.TorStats)

    security_level = config.get('general.security_level', 1)
    use_existing_tor = config.get('tor.use_existing_tor', False)

    if not offline_mode:
        # we need to setup tor for use
        _setup_online_mode(use_existing_tor, net, security_level)

    _show_info_messages()

    events.event('init', threaded=False)
    events.event('daemon_start')
    if config.get('transports.lan', True):
        Thread(target=LANServer(shared_state).start_server,
               daemon=True).start()
        LANManager(shared_state).start()
    if config.get('transports.sneakernet', True):
        Thread(target=sneakernet_import_thread, daemon=True).start()

    Thread(target=statistics_reporter, args=[shared_state], daemon=True).start()

    communicator.startCommunicator(shared_state)

    clean_ephemeral_services()

    if not offline_mode and not use_existing_tor:
        net.killTor()
    else:
        try:
            os.remove(filepaths.tor_hs_address_file)
        except FileNotFoundError:
            pass

    better_sleep(5)

    cleanup.delete_run_files()
    if security_level >= 2:
        filenuke.nuke.clean_tree(identifyhome.identify_home())


def _ignore_sigint(sig, frame):  # pylint: disable=W0612,W0613
    """Space intentionally left blank."""
    return


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
        logger.fatal('Cannot start. Daemon is already running,'
                     + ' or it did not exit cleanly.\n'
                     + ' (if you are sure that there is not a daemon running,'
                     + f' delete {filepaths.lock_file} & try again).',
                     terminal=True)
    else:
        if not onionrvalues.DEVELOPMENT_MODE:
            lock_file = open(filepaths.lock_file, 'w')
            lock_file.write('delete at your own risk')
            lock_file.close()

        # Start Onionr daemon
        daemon()

        try:
            os.remove(filepaths.lock_file)
        except FileNotFoundError:
            pass


start.onionr_help = "Start Onionr node "  # type: ignore
start.onionr_help += "(public and clients API servers)"  # type: ignore
