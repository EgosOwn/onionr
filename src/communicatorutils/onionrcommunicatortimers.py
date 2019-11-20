'''
    Onionr - Private P2P Communication

    This file contains timer control for the communicator
'''
from __future__ import annotations  # thank you python, very cool
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

import uuid
import threading

import onionrexceptions, logger

from typing import TYPE_CHECKING
from typing import Callable, NewType, Iterable
if TYPE_CHECKING:
    from communicator import OnionrCommunicatorDaemon

CallFreqSeconds = NewType('CallFreqSeconds', int)

class OnionrCommunicatorTimers:
    def __init__(self, daemon_inst: OnionrCommunicatorDaemon, 
                timer_function: Callable, frequency: CallFreqSeconds, 
                make_thread:bool=True, thread_amount:int=1, max_threads:int=5, 
                requires_peer:bool=False, my_args:Iterable=[]):
        self.timer_function = timer_function
        self.frequency = frequency
        self.thread_amount = thread_amount
        self.make_thread = make_thread
        self.requires_peer = requires_peer
        self.daemon_inst = daemon_inst
        self.max_threads = max_threads
        self.args = my_args

        self.daemon_inst.timers.append(self)
        self.count = 0

    def processTimer(self):

        # mark how many instances of a thread we have (decremented at thread end)
        try:
            self.daemon_inst.threadCounts[self.timer_function.__name__]
        except KeyError:
            self.daemon_inst.threadCounts[self.timer_function.__name__] = 0

        # execute thread if it is time, and we are not missing *required* online peer
        if self.count == self.frequency and not self.daemon_inst.shutdown:
            try:
                if self.requires_peer and len(self.daemon_inst.onlinePeers) == 0:
                    raise onionrexceptions.OnlinePeerNeeded
            except onionrexceptions.OnlinePeerNeeded:
                return
            else:
                if self.make_thread:
                    for i in range(self.thread_amount):
                        if self.daemon_inst.threadCounts[self.timer_function.__name__] >= self.max_threads:
                            logger.debug('%s is currently using the maximum number of threads, not starting another.' % self.timer_function.__name__)
                        else:
                            self.daemon_inst.threadCounts[self.timer_function.__name__] += 1
                            newThread = threading.Thread(target=self.timer_function, args=self.args, daemon=True, 
                                                        name=self.timer_function.__name__ + ' - ' + str(uuid.uuid4()))
                            newThread.start()
                else:
                    self.timer_function()
            self.count = -1 # negative 1 because its incremented at bottom
        self.count += 1
