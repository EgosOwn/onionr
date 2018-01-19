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
import subprocess, os, random, sys
class NetController:
    '''NetController
    This class handles hidden service setup on Tor and I2P
    '''
    def __init__(self, hsPort):
        self.torConfigLocation = 'data/torrc'
        self.readyState = False
        self.socksPort = random.randint(1024, 65535)
        self.hsPort = hsPort
        self.myID = ''
        if os.path.exists(self.torConfigLocation):
            torrc = open(self.torConfigLocation, 'r')
            if not self.hsPort in torrc.read():
                os.remove(self.torConfigLocation)
        return
    def generateTorrc(self):
        if os.path.exists(self.torConfigLocation):
            os.remove(self.torConfigLocation)
        torrcData = '''SOCKSPORT ''' + str(self.socksPort) + '''
HiddenServiceDir data/hs/
HiddenServicePort 80 127.0.0.1:''' + str(self.hsPort) + '''
        '''
        torrc = open(self.torConfigLocation, 'w')
        torrc.write(torrcData)
        torrc.close()
        return

    def startTor(self):
        self.generateTorrc()
        tor = subprocess.Popen(['tor', '-f', self.torConfigLocation], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(tor.stdout.readline, b''):
            if 'Bootstrapped 100%: Done' in line.decode():
                break
        print('Finished starting Tor')
        self.readyState = True
        myID = open('data/hs/hostname', 'r')
        self.myID = myID.read()
        myID.close()
        return