'''
    Onionr - P2P Microblogging Platform & Social network

    OnionrUtils offers various useful functions to Onionr networking.
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
from onionrutils import basicrequests
def checkNetwork(torPort=0):
    '''Check if we are connected to the internet (through Tor)'''
    retData = False
    connectURLs = []
    try:
        with open('static-data/connect-check.txt', 'r') as connectTest:
            connectURLs = connectTest.read().split(',')

        for url in connectURLs:
            if basicrequests.do_get_request(url, port=torPort, ignoreAPI=True) != False:
                retData = True
                break
    except FileNotFoundError:
        pass
    return retData