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
import onionrexceptions
from defusedxml import minidom

class OnionrCommunicatorDaemon:
    def __init__(self, debug, developmentMode):
        self.timers = []
        self._core = core.Core()
        self.nistSaltTimestamp = 0
        self.powSalt = 0
        self.delay = 1
        self.proxyPort = sys.argv[2]

        self.onlinePeers = []

        self.threadCounts = {}

        self.shutdown = False

        # Clear the daemon queue for any dead messages
        if os.path.exists(self._core.queueDB):
            self._core.clearDaemonQueue()

        # Loads in and starts the enabled plugins
        plugins.reload()

        # Print nice header thing :)
        if config.get('general.display_header', True):
            self.header()

        if debug or developmentMode:
            OnionrCommunicatorTimers(self, self.heartbeat, 10)

        self.getOnlinePeers()
        OnionrCommunicatorTimers(self, self.daemonCommands, 5)
        OnionrCommunicatorTimers(self, self.detectAPICrash, 12)
        OnionrCommunicatorTimers(self, self.getOnlinePeers, 60)

        # Main daemon loop, mainly for calling timers, do not do any complex operations here
        while not self.shutdown:
            for i in self.timers:
                i.processTimer()
            time.sleep(self.delay)
        logger.info('Goodbye.')

    def decrementThreadCount(self, threadName):
        if self.threadCounts[threadName] > 0:
            self.threadCounts[threadName] -= 1

    def getOnlinePeers(self):
        '''Manages the self.onlinePeers attribute list'''
        logger.info('Refreshing peer pool.')
        maxPeers = 4
        needed = maxPeers - len(self.onlinePeers)

        for i in range(needed):
            self.connectNewPeer()
        self.decrementThreadCount('getOnlinePeers')

    def connectNewPeer(self, peer=''):
        '''Adds a new random online peer to self.onlinePeers'''
        retData = False
        if peer != '':
            if self._core._utils.validateID(peer):
                peerList = [peer]
            else:
                raise onionrexceptions.InvalidAddress('Will not attempt connection test to invalid address')
        else:
            peerList = self._core.listAdders()

        if len(peerList) == 0:
            peerList.extend(self._core.bootstrapList)

        for address in peerList:
            if self.peerAction(address, 'ping') == 'pong!':
                logger.info('connected to ' + address)
                self.onlinePeers.append(address)
                retData = address
                break
            else:
                logger.debug('failed to connect to ' + address)
        else:
            logger.warn('Could not connect to any peer')
        return retData

    def heartbeat(self):
        '''Show a heartbeat debug message'''
        logger.debug('Communicator heartbeat')
        self.decrementThreadCount('heartbeat')

    def daemonCommands(self):
        '''process daemon commands from daemonQueue'''
        cmd = self._core.daemonQueue()

        if cmd is not False:
            if cmd[0] == 'shutdown':
                self.shutdown = True
            elif cmd[0] == 'announceNode':
                self.announce(cmd[1])
            elif cmd[0] == 'runCheck':
                logger.debug('Status check; looks good.')
                open('data/.runcheck', 'w+').close()
            elif cmd[0] == 'connectedPeers':
                self.printOnlinePeers()
            else:
                logger.info('Recieved daemonQueue command:' + cmd[0])
        self.decrementThreadCount('daemonCommands')

    def printOnlinePeers(self):
        '''logs online peer list'''
        if len(self.onlinePeers) == 0:
            logger.warn('No online peers')
            return
        for i in self.onlinePeers:
            logger.info(self.onlinePeers[i])

    def announce(self, peer):
        '''Announce to peers'''
        announceCount = 0
        announceAmount = 2
        for peer in self._core.listAdders():
            announceCount += 1
            if self.peerAction(peer, 'announce', self._core.hsAdder) == 'Success':
                logger.info('Successfully introduced node to ' + peer)
                break
            else:
                if announceCount == announceAmount:
                    logger.warn('Could not introduce node. Try again soon')
                    break

    def peerAction(self, peer, action, data=''):
        '''Perform a get request to a peer'''
        logger.info('Performing ' + action + ' with ' + peer + ' on port ' + str(self.proxyPort))
        retData = self._core._utils.doGetRequest('http://' + peer + '/public/?action=' + action + '&data=' + data, port=self.proxyPort)
        if retData == False:
            self.onlinePeers.remove(peer)
            self.getOnlinePeers() # Will only add a new peer to pool if needed
        return retData

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
        self.decrementThreadCount('detectAPICrash')

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
if config.get('general.dev_mode', True):
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
