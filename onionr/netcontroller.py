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

import subprocess, os, random, sys, logger, time, signal, config, base64, socket
from stem.control import Controller
from onionrblockapi import Block
from dependencies import secrets
from shutil import which

def getOpenPort():
    # taken from (but modified) https://stackoverflow.com/a/2838309
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port

def torBinary():
    '''Return tor binary path or none if not exists'''
    torPath = './tor'
    if not os.path.exists(torPath):
        torPath = which('tor')
    return torPath

class NetController:
    '''
        This class handles hidden service setup on Tor and I2P
    '''

    def __init__(self, hsPort, apiServerIP='127.0.0.1'):
        try:
            self.dataDir = os.environ['ONIONR_HOME']
            if not self.dataDir.endswith('/'):
                self.dataDir += '/'
        except KeyError:
            self.dataDir = 'data/'

        self.torConfigLocation = self.dataDir + 'torrc'
        self.readyState = False
        self.socksPort = getOpenPort()
        self.hsPort = hsPort
        self._torInstnace = ''
        self.myID = ''
        self.apiServerIP = apiServerIP

        if os.path.exists('./tor'):
            self.torBinary = './tor'
        elif os.path.exists('/usr/bin/tor'):
            self.torBinary = '/usr/bin/tor'
        else:
            self.torBinary = 'tor'

        config.reload()
        '''
            if os.path.exists(self.torConfigLocation):
                torrc = open(self.torConfigLocation, 'r')
                if not str(self.hsPort) in torrc.read():
                    os.remove(self.torConfigLocation)
                torrc.close()
        '''

        return

    def generateTorrc(self):
        '''
            Generate a torrc file for our tor instance
        '''
        hsVer = '# v2 onions'
        if config.get('tor.v3onions'):
            hsVer = 'HiddenServiceVersion 3'
            logger.debug('Using v3 onions')

        if os.path.exists(self.torConfigLocation):
            os.remove(self.torConfigLocation)

        # Set the Tor control password. Meant to make it harder to manipulate our Tor instance
        plaintext = base64.b64encode(os.urandom(50)).decode()
        config.set('tor.controlpassword', plaintext, savefile=True)
        config.set('tor.socksport', self.socksPort, savefile=True)

        controlPort = getOpenPort()

        config.set('tor.controlPort', controlPort, savefile=True)

        hashedPassword = subprocess.Popen([self.torBinary, '--hash-password', plaintext], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(hashedPassword.stdout.readline, b''):
            password = line.decode()
            if 'warn' not in password:
                break

        torrcData = '''SocksPort ''' + str(self.socksPort) + '''
DataDirectory ''' + self.dataDir + '''tordata/
CookieAuthentication 1
ControlPort ''' + str(controlPort) + '''
HashedControlPassword ''' + str(password) + '''
        '''
        if config.get('general.security_level') == 0:
            torrcData += '''\nHiddenServiceDir ''' + self.dataDir + '''hs/
\n''' + hsVer + '''\n
HiddenServicePort 80 ''' + self.apiServerIP + ''':''' + str(self.hsPort)

        torrc = open(self.torConfigLocation, 'w')
        torrc.write(torrcData)
        torrc.close()

        return

    def startTor(self):
        '''
            Start Tor with onion service on port 80 & socks proxy on random port
        '''

        self.generateTorrc()

        if os.path.exists('./tor'):
            self.torBinary = './tor'
        elif os.path.exists('/usr/bin/tor'):
            self.torBinary = '/usr/bin/tor'
        else:
            self.torBinary = 'tor'

        try:
            tor = subprocess.Popen([self.torBinary, '-f', self.torConfigLocation], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            logger.fatal("Tor was not found in your path or the Onionr directory. Please install Tor and try again.")
            sys.exit(1)
        else:
            # Test Tor Version
            torVersion = subprocess.Popen([self.torBinary, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in iter(torVersion.stdout.readline, b''):
                if 'Tor 0.2.' in line.decode():
                    logger.warn("Running 0.2.x Tor series, no support for v3 onion peers")
                    break
            torVersion.kill()

        # wait for tor to get to 100% bootstrap
        try:
            for line in iter(tor.stdout.readline, b''):
                if 'Bootstrapped 100%: Done' in line.decode():
                    break
                elif 'Opening Socks listener' in line.decode():
                    logger.debug(line.decode().replace('\n', ''))
            else:
                logger.fatal('Failed to start Tor. Maybe a stray instance of Tor used by Onionr is still running?')
                return False
        except KeyboardInterrupt:
            logger.fatal('Got keyboard interrupt.', timestamp = false, level = logger.LEVEL_IMPORTANT)
            return False
        
        logger.debug('Finished starting Tor.', timestamp=True)
        self.readyState = True

        try:
            myID = open(self.dataDir + 'hs/hostname', 'r')
            self.myID = myID.read().replace('\n', '')
            myID.close()
        except FileNotFoundError:
            self.myID = ""

        torPidFile = open(self.dataDir + 'torPid.txt', 'w')
        torPidFile.write(str(tor.pid))
        torPidFile.close()

        return True

    def killTor(self):
        '''
            Properly kill tor based on pid saved to file
        '''

        try:
            pid = open(self.dataDir + 'torPid.txt', 'r')
            pidN = pid.read()
            pid.close()
        except FileNotFoundError:
            return

        try:
            int(pidN)
        except:
            return

        try:
            os.kill(int(pidN), signal.SIGTERM)
            os.remove(self.dataDir + 'torPid.txt')
        except ProcessLookupError:
            pass
        except FileNotFoundError:
            pass

        return
