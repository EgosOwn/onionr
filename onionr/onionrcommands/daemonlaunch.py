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
import onionr, api, logger, communicator
import onionrevents as events
from netcontroller import NetController
def daemon(o_inst):
    '''
        Starts the Onionr communication daemon
    '''

    # remove runcheck if it exists
    if os.path.isfile('%s/.runcheck' % (o_inst.onionrCore.dataDir,)):
        logger.debug('Runcheck file found on daemon start, deleting in advance.')
        os.remove('%s/.runcheck' % (o_inst.onionrCore.dataDir,))

    Thread(target=api.API, args=(o_inst, o_inst.debug, onionr.API_VERSION)).start()
    Thread(target=api.PublicAPI, args=[o_inst.getClientApi()]).start()
    try:
        time.sleep(0)
    except KeyboardInterrupt:
        logger.debug('Got keyboard interrupt, shutting down...')
        time.sleep(1)
        o_inst.onionrUtils.localCommand('shutdown')

    apiHost = ''
    while apiHost == '':
        try:
            with open(o_inst.onionrCore.publicApiHostFile, 'r') as hostFile:
                apiHost = hostFile.read()
        except FileNotFoundError:
            pass
        time.sleep(0.5)
    #onionr.Onionr.setupConfig('data/', self = o_inst)

    if o_inst._developmentMode:
        logger.warn('DEVELOPMENT MODE ENABLED (NOT RECOMMENDED)', timestamp = False)
    net = NetController(o_inst.onionrCore.config.get('client.public.port', 59497), apiServerIP=apiHost)
    logger.debug('Tor is starting...')
    if not net.startTor():
        o_inst.onionrUtils.localCommand('shutdown')
        sys.exit(1)
    if len(net.myID) > 0 and o_inst.onionrCore.config.get('general.security_level', 1) == 0:
        logger.debug('Started .onion service: %s' % (logger.colors.underline + net.myID))
    else:
        logger.debug('.onion service disabled')
    logger.debug('Using public key: %s' % (logger.colors.underline + o_inst.onionrCore._crypto.pubKey))
    time.sleep(1)

    o_inst.onionrCore.torPort = net.socksPort
    communicatorThread = Thread(target=communicator.startCommunicator, args=(o_inst, str(net.socksPort)))
    communicatorThread.start()
    
    while o_inst.communicatorInst is None:
        time.sleep(0.1)

    # print nice header thing :)
    if o_inst.onionrCore.config.get('general.display_header', True):
        o_inst.header()

    # print out debug info
    o_inst.version(verbosity = 5, function = logger.debug)
    logger.debug('Python version %s' % platform.python_version())

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
    o_inst.onionrCore.daemonQueueAdd('shutdown')
    o_inst.onionrUtils.localCommand('shutdown')

    net.killTor()
    time.sleep(3)
    o_inst.deleteRunFiles()
    return

def _ignore_sigint(sig, frame):
    return

def kill_daemon(o_inst):
    '''
        Shutdown the Onionr daemon
    '''

    logger.warn('Stopping the running daemon...', timestamp = False)
    try:
        events.event('daemon_stop', onionr = o_inst)
        net = NetController(o_inst.onionrCore.config.get('client.port', 59496))
        try:
            o_inst.onionrCore.daemonQueueAdd('shutdown')
        except sqlite3.OperationalError:
            pass

        net.killTor()
    except Exception as e:
        logger.error('Failed to shutdown daemon.', error = e, timestamp = False)
    return

def start(o_inst, input = False, override = False):
    if os.path.exists('.onionr-lock') and not override:
        logger.fatal('Cannot start. Daemon is already running, or it did not exit cleanly.\n(if you are sure that there is not a daemon running, delete .onionr-lock & try again).')
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