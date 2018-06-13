#!/usr/bin/env python3
'''
    Onionr - P2P Microblogging Platform & Social network.

    This file contains both the OnionrCommunicate class for communcating with peers
    and code to operate as a daemon, getting commands from the command queue database (see core.Core.daemonQueue)
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
import sys, os, core, config, onionrblockapi as block, requests, time, logger, threading, onionrplugins as plugins
from defusedxml import minidom

class OnionrCommunicatorDaemon:
    def __init__(self, debug, developmentMode):
        self.timers = []
        self._core = core.Core()
        self.nistSaltTimestamp = 0
        self.powSalt = 0
        self.delay = 1
        self.proxyPort = sys.argv[2]

        self.threadCounts = {}

        self.shutdown = False
        
        # Clear the daemon queue for any dead messages
        if os.path.exists(self._core.queueDB):
            self._core.clearDaemonQueue()

        # Loads in and starts the enabled plugins
        plugins.reload()

        # Print nice header thing :)
        if config.get('display_header', True):
            self.header()

        if debug or developmentMode:
            OnionrCommunicatorTimers(self, self.heartbeat, 10)

        OnionrCommunicatorTimers(self, self.daemonCommands, 5)
        OnionrCommunicatorTimers(self, self.detectAPICrash, 12)

        # Main daemon loop, mainly for calling timers, do not do any complex operations here
        while not self.shutdown:
            for i in self.timers:
                i.processTimer()
            time.sleep(self.delay)
        logger.info('Goodbye.')
        
    def heartbeat(self):
        '''Show a heartbeat debug message'''
        logger.debug('Communicator heartbeat')
        self.threadCounts['heartbeat'] -= 1

    def daemonCommands(self):
        '''process daemon commands from daemonQueue'''
        cmd = self._core.daemonQueue()

        if cmd is not False:
            if cmd[0] == 'shutdown':
                self.shutdown = True
            elif cmd[0] == 'announce':
                self.announce(cmd[1])
            else:
                logger.info('Recieved daemonQueue command:' + cmd[0])
        self.threadCounts['daemonCommands'] -= 1
    
    def announce(self, peer):
        '''Announce to peers'''
        for peer in self._core.listAdders():
            self.peerAction(peer, 'announce', self._core.hsAdder)
    
    def peerAction(self, peer, action, data=''):
        '''Perform a get request to a peer'''
        return self._core._utils.doGetRequest('http://' + peer + '/public/?action=' + action + '&data=' + data, port=self.proxyPort)

    def detectAPICrash(self):
        '''exit if the api server crashes/stops'''
        if self._core._utils.localCommand('ping') != 'pong':
            for i in range(4):
                if self._core._utils.localCommand('ping') == 'pong':
                    break # break for loop
                time.sleep(1)
            else:
                # This executes if the api is NOT detected to be running
                logger.error('Daemon detected API crash (or otherwise unable to reach API after long time), stopping...')
                self.shutdown = True
        self.threadCounts['detectAPICrash'] -= 1

    def header(self, message = logger.colors.fg.pink + logger.colors.bold + 'Onionr' + logger.colors.reset + logger.colors.fg.pink + ' has started.'):
        if os.path.exists('static-data/header.txt'):
            with open('static-data/header.txt', 'rb') as file:
                # only to stdout, not file or log or anything
                print(file.read().decode().replace('P', logger.colors.fg.pink).replace('W', logger.colors.reset + logger.colors.bold).replace('G', logger.colors.fg.green).replace('\n', logger.colors.reset + '\n'))
                logger.info(logger.colors.fg.lightgreen + '-> ' + str(message) + logger.colors.reset + logger.colors.fg.lightgreen + ' <-\n')
    
class OnionrCommunicatorTimers:
    def __init__(self, daemonInstance, timerFunction, frequency, makeThread=True, threadAmount=1, maxThreads=5):
        self.timerFunction = timerFunction
        self.frequency = frequency
        self.threadAmount = threadAmount
        self.makeThread = makeThread
        self.daemonInstance = daemonInstance
        self.maxThreads = maxThreads
        self._core = self.daemonInstance._core

        self.daemonInstance.timers.append(self)
        self.count = 0

    def processTimer(self):
        self.count += 1
        try:
            self.daemonInstance.threadCounts[self.timerFunction.__name__]
        except KeyError:
            self.daemonInstance.threadCounts[self.timerFunction.__name__] = 0

        if self.count == self.frequency:
            if self.makeThread:
                for i in range(self.threadAmount):
                    if self.daemonInstance.threadCounts[self.timerFunction.__name__] >= self.maxThreads:
                        logger.warn(self.timerFunction.__name__ + ' has too many current threads to start anymore.')
                    else:
                        self.daemonInstance.threadCounts[self.timerFunction.__name__] += 1
                        newThread = threading.Thread(target=self.timerFunction)
                        newThread.start()
            else:
                self.timerFunction()
            self.count = 0


shouldRun = False
debug = True
developmentMode = False
if config.get('devmode', True):
    developmentMode = True
try:
    if sys.argv[1] == 'run':
        shouldRun = True
except IndexError:
    pass
if shouldRun:
    try:
        OnionrCommunicatorDaemon(debug, developmentMode)
    except KeyboardInterrupt:
        sys.exit(1)
        pass
    except Exception as e:
        logger.error('Error occured in Communicator', error = e, timestamp = False)