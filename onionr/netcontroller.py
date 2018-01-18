'''
    Onionr - P2P Microblogging Platform & Social network

    Netcontroller library, used to control/work with Tor/I2P and send requests through them
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
import subprocess
class NetController:
    '''NetController
    This class handles hidden service setup on Tor and I2P
    '''
    def __init__(self, hsPort, socksPort):
        self.torConfigLocation = 'data/torrc'
        self.readyState = False
        return
    def generateTorrc(self):
        torrcData = '''SOCKSPORT 

        '''
        return

    def startTor(self):
        subprocess.Popen(['tor', '-f ' + self.torConfigLocation])
        return