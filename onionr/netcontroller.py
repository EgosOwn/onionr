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

import subprocess, os, random, sys, logger, time, signal
from onionrblockapi import Block

class NetController:
    '''
        This class handles hidden service setup on Tor and I2P
    '''

    def __init__(self, hsPort):
        self.torConfigLocation = 'data/torrc'
        self.readyState = False
        self.socksPort = random.randint(1024, 65535)
        self.hsPort = hsPort
        self._torInstnace = ''
        self.myID = ''
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

        if os.path.exists(self.torConfigLocation):
            os.remove(self.torConfigLocation)
        torrcData = '''SocksPort ''' + str(self.socksPort) + '''
HiddenServiceDir data/hs/
HiddenServicePort 80 127.0.0.1:''' + str(self.hsPort) + '''
DataDirectory data/tordata/
        '''
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
            torBinary = './tor'
        elif os.path.exists('/usr/bin/tor'):
            torBinary = '/usr/bin/tor'
        else:
            torBinary = 'tor'

        try:
            tor = subprocess.Popen([torBinary, '-f', self.torConfigLocation], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            logger.fatal("Tor was not found in your path or the Onionr directory. Please install Tor and try again.")
            sys.exit(1)
        else:
            # Test Tor Version
            torVersion = subprocess.Popen([torBinary, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
            logger.fatal("Got keyboard interrupt.")
            return False

        logger.debug('Finished starting Tor.', timestamp=True)
        self.readyState = True

        myID = open('data/hs/hostname', 'r')
        self.myID = myID.read().replace('\n', '')
        myID.close()

        torPidFile = open('data/torPid.txt', 'w')
        torPidFile.write(str(tor.pid))
        torPidFile.close()

        return True

    def killTor(self):
        '''
            Properly kill tor based on pid saved to file
        '''

        try:
            pid = open('data/torPid.txt', 'r')
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
            os.remove('data/torPid.txt')
        except ProcessLookupError:
            pass
        except FileNotFoundError:
            pass

        return
