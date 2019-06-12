'''
    Onionr - Private P2P Communication

    This file contains timer control for the communicator
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
import threading, onionrexceptions, logger
class OnionrCommunicatorTimers:
    def __init__(self, daemonInstance, timerFunction, frequency, makeThread=True, threadAmount=1, maxThreads=5, requiresPeer=False, myArgs=[]):
        self.timerFunction = timerFunction
        self.frequency = frequency
        self.threadAmount = threadAmount
        self.makeThread = makeThread
        self.requiresPeer = requiresPeer
        self.daemonInstance = daemonInstance
        self.maxThreads = maxThreads
        self._core = self.daemonInstance._core
        self.args = myArgs

        self.daemonInstance.timers.append(self)
        self.count = 0

    def processTimer(self):

        # mark how many instances of a thread we have (decremented at thread end)
        try:
            self.daemonInstance.threadCounts[self.timerFunction.__name__]
        except KeyError:
            self.daemonInstance.threadCounts[self.timerFunction.__name__] = 0

        # execute thread if it is time, and we are not missing *required* online peer
        if self.count == self.frequency and not self.daemonInstance.shutdown:
            try:
                if self.requiresPeer and len(self.daemonInstance.onlinePeers) == 0:
                    raise onionrexceptions.OnlinePeerNeeded
            except onionrexceptions.OnlinePeerNeeded:
                pass
            else:
                if self.makeThread:
                    for i in range(self.threadAmount):
                        if self.daemonInstance.threadCounts[self.timerFunction.__name__] >= self.maxThreads:
                            logger.debug('%s is currently using the maximum number of threads, not starting another.' % self.timerFunction.__name__)
                        else:
                            self.daemonInstance.threadCounts[self.timerFunction.__name__] += 1
                            newThread = threading.Thread(target=self.timerFunction, args=self.args)
                            newThread.start()
                else:
                    self.timerFunction()
            self.count = -1 # negative 1 because its incremented at bottom
        self.count += 1
