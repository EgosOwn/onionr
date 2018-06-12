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
import sys, core, config, onionrblockapi as block, requests, time, logger
from defusedxml import minidom

class OnionrCommunicatorDaemon:
    def __init__(self, debug, developmentMode):
        self.timers = []
        self._core = core.Core()
        self.nistSaltTimestamp = 0
        self.powSalt = 0
        self.delay = 1

        OnionrCommunicatorTimers(self.timers, self.heartbeat, 1)

        while True:
            time.sleep(self.delay)
            for i in self.timers:
                i.processTimer()
    
    def heartbeat(self):
        logger.debug('Communicator heartbeat')
    
class OnionrCommunicatorTimers:
    def __init__(self, timerList, timerFunction, frequency):
        self.timerFunction = timerFunction
        self.frequency = frequency

        timerList.append(self)
        self.count = 0
    def processTimer(self):
        self.count += 1
        if self.count == self.frequency:
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