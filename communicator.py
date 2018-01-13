#!/usr/bin/env python3
'''
    Onionr - P2P Microblogging Platform & Social network. Run with 'help' for usage.
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
import sqlite3, requests, hmac, hashlib, time
import core
class OnionrCommunicate:
    def __init__(self):
        self._core = core.Core()
        while True:
            print('Onionr daemon running')
            time.sleep(2)
        return
    def getRemotePeerKey(self, peerID):
        '''This function contacts a peer and gets their main PGP key.
        This is safe because Tor or I2P is used, but it does not insure that the person is who they say they are
        '''
        url = 'http://' + peerID + '/public/?action=getPGP'
        r = requests.get(url, headers=headers)
        response = r.text
        return response



OnionrCommunicate()