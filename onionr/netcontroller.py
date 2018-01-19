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
import subprocess, os
class NetController:
    '''NetController
    This class handles hidden service setup on Tor and I2P
    '''
    def __init__(self, hsPort):
        self.torConfigLocation = 'data/torrc'
        self.readyState = False
        self.socksPort = socksPort
        self.hsPort = hsPort
        if os.path.exists(self.torConfigLocation):
            torrc = open(self.torConfigLocation, 'r')
            if not self.hsPort in torrc.read():
                os.remove(self.torConfigLocation)
        return
    def generateTorrc(self):
        if os.path.exists(self.torConfigLocation):
            os.remove(self.torConfigLocation)
        torrcData = '''SOCKSPORT ''' + self.socksPort + '''
HiddenServiceData data/hs/
HiddenServicePort 80 127.0.0.1:''' + self.hsPort + '''
        '''
        torrc = open(self.torConfigLocation, 'w')
        torrc.write(torrcData)
        torrc.close()
        return

    def startTor(self):
        if not os.path.exists(self.torConfigLocation):
            self.generateTorrc()
        subprocess.Popen(['tor', '-f ' + self.torConfigLocation])
        return