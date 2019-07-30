'''
    Onionr - Private P2P Communication

    launch the api server and communicator
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

import os, time, sys, platform, sqlite3, signal
from threading import Thread
import onionr, apiservers, logger, communicator
import onionrevents as events
from netcontroller import NetController
from onionrutils import localcommand
import filepaths
from coredb import daemonqueue
from onionrcrypto import getourkeypair
from utils import hastor, logoheader

def _proper_shutdown(o_inst):
    localcommand.local_command('shutdown')
    sys.exit(1)

def daemon(o_inst):
    '''
        Starts the Onionr communication daemon
    '''
    if not hastor.has_tor():
        logger.error("Tor is not present in system path or Onionr directory", terminal=True)
        sys.exit(1)

    # remove runcheck if it exists
    if os.path.isfile(filepaths.run_check_file):
        logger.debug('Runcheck file found on daemon start, deleting in advance.')
        os.remove(filepaths.run_check_file)

    Thread(target=apiservers.ClientAPI, args=(o_inst, o_inst.debug, onionr.API_VERSION), daemon=True).start()
    Thread(target=apiservers.PublicAPI, args=[o_inst.getClientApi()], daemon=True).start()

    apiHost = ''
    while apiHost == '':
        try:
            with open(filepaths.public_API_host_file, 'r') as hostFile:
                apiHost = hostFile.read()
        except FileNotFoundError:
            pass
        time.sleep(0.5)
    #onionr.Onionr.setupConfig('data/', self = o_inst)

    logger.raw('', terminal=True)
    # print nice header thing :)
    if o_inst.config.get('general.display_header', True):
        logoheader.header()
    o_inst.version(verbosity = 5, function = logger.info)
    logger.debug('Python version %s' % platform.python_version())

    if o_inst._developmentMode:
        logger.warn('Development mode enabled', timestamp = False, terminal=True)
    net = NetController(o_inst.config.get('client.public.port', 59497), apiServerIP=apiHost)
    logger.info('Tor is starting...', terminal=True)
    if not net.startTor():
        localcommand.local_command('shutdown')
        sys.exit(1)
    if len(net.myID) > 0 and o_inst.config.get('general.security_level', 1) == 0:
        logger.debug('Started .onion service: %s' % (logger.colors.underline + net.myID))
    else:
        logger.debug('.onion service disabled')
    logger.info('Using public key: %s' % (logger.colors.underline + getourkeypair.get_keypair()[0][:52]), terminal=True)

    try:
        time.sleep(1)
    except KeyboardInterrupt:
        _proper_shutdown(o_inst)

    o_inst.torPort = net.socksPort
    communicatorThread = Thread(target=communicator.startCommunicator, args=(o_inst, str(net.socksPort)), daemon=True)
    communicatorThread.start()
    
    while o_inst.communicatorInst is None:
        time.sleep(0.1)

    logger.debug('Started communicator.')

    events.event('daemon_start', onionr = o_inst)
    while True:
        try:
            time.sleep(3)
        except KeyboardInterrupt:
            o_inst.communicatorInst.shutdown = True
        finally:
            # Debug to print out used FDs (regular and net)
            #proc = psutil.Process()
            #print('api-files:',proc.open_files(), len(psutil.net_connections()))
            # Break if communicator process ends, so we don't have left over processes
            if o_inst.communicatorInst.shutdown:
                break
            if o_inst.killed:
                break # Break out if sigterm for clean exit

    signal.signal(signal.SIGINT, _ignore_sigint)
    daemonqueue.daemon_queue_add('shutdown')
    localcommand.local_command('shutdown')

    net.killTor()
    time.sleep(5) # Time to allow threads to finish, if not any "daemon" threads will be slaughtered http://docs.python.org/library/threading.html#threading.Thread.daemon
    o_inst.deleteRunFiles()
    return

def _ignore_sigint(sig, frame):
    return

def kill_daemon(o_inst):
    '''
        Shutdown the Onionr daemon
    '''

    logger.warn('Stopping the running daemon...', timestamp = False, terminal=True)
    try:
        events.event('daemon_stop', onionr = o_inst)
        net = NetController(o_inst.config.get('client.port', 59496))
        try:
            daemonqueue.daemon_queue_add('shutdown')
        except sqlite3.OperationalError:
            pass

        net.killTor()
    except Exception as e:
        logger.error('Failed to shutdown daemon: ' + str(e), error = e, timestamp = False, terminal=True)
    return

def start(o_inst, input = False, override = False):
    if os.path.exists('.onionr-lock') and not override:
        logger.fatal('Cannot start. Daemon is already running, or it did not exit cleanly.\n(if you are sure that there is not a daemon running, delete .onionr-lock & try again).', terminal=True)
    else:
        if not o_inst.debug and not o_inst._developmentMode:
            lockFile = open('.onionr-lock', 'w')
            lockFile.write('')
            lockFile.close()
        o_inst.running = True
        o_inst.daemon()
        o_inst.running = False
        if not o_inst.debug and not o_inst._developmentMode:
            try:
                os.remove('.onionr-lock')
            except FileNotFoundError:
                pass