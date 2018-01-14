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
import sqlite3, requests, hmac, hashlib, time, sys
import core
class OnionrCommunicate:
    def __init__(self):
        ''' OnionrCommunicate

        This class handles communication with nodes in the Onionr network.
        '''
        self._core = core.Core()
        while True:
            command = self._core.daemonQueue()
            print('Daemon heartbeat')
            if command != False:
                if command[0] == 'shutdown':
                    print('Daemon recieved exit command.')
                    break
            time.sleep(1)
        return
    def getRemotePeerKey(self, peerID):
        '''This function contacts a peer and gets their main PGP key.
        
        This is safe because Tor or I2P is used, but it does not ensure that the person is who they say they are
        '''
        url = 'http://' + peerID + '/public/?action=getPGP'
        r = requests.get(url, headers=headers)
        response = r.text
        return response
shouldRun = False
try:
    if sys.argv[1] == 'run':
        shouldRun = True
except IndexError:
    pass
if shouldRun:
    OnionrCommunicate()