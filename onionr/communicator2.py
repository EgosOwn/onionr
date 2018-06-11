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
import core, config, onionrblockapi as block, requests, xml
class OnionrCommunicatorDaemon:
    def __init__(self, debug, developmentMode):
        self.timers = [] # list of tuples, function, time in seconds
        self._core = core.Core()

        self.nistSalt = 0
        return
    
    def getNistTimeStamp(self):
        curTime = self._core._utils.getCurrentHourEpoch
        data = doGetRequest('https://beacon.nist.gov/rest/record/' + str(curTime))
        

    def doGetRequest(self, url, port=sys.argv[2], proxyType='tor'):
        '''
        Do a get request through a local tor or i2p instance
        '''
        if proxyType == 'tor':
            proxies = {'http': 'socks5://127.0.0.1:' + str(port), 'https': 'socks5://127.0.0.1:' + str(port)}
        elif proxyType == 'i2p':
            proxies = {'http': 'http://127.0.0.1:4444'}
        else:
            return
        headers = {'user-agent': 'PyOnionr'}
        r = requests.get(url, headers=headers, proxies=proxies, allow_redirects=False, timeout=(15, 30))

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
