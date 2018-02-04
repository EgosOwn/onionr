#!/usr/bin/env python3
'''
    Onionr - P2P Microblogging Platform & Social network.

    Onionr is the name for both the protocol and the original/reference software.

    Run with 'help' for usage.
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
import sys, os, configparser, base64, random, getpass, shutil, subprocess, requests, time, logger, platform
import api, core
from onionrutils import OnionrUtils
from netcontroller import NetController

try:
    from urllib3.contrib.socks import SOCKSProxyManager
except ImportError:
    raise Exception("You need the PySocks module (for use with socks5 proxy to use Tor)")

ONIONR_VERSION = '0.0.0' # for debugging and stuff
API_VERSION = '1' # increments of 1; only change when something fundemental about how the API works changes. This way other nodes knows how to communicate without learning too much information about you.

class Onionr:
    def __init__(self):
        '''
            Main Onionr class. This is for the CLI program, and does not handle much of the logic.
            In general, external programs and plugins should not use this class.
        '''
        try:
            os.chdir(sys.path[0])
        except FileNotFoundError:
            pass

        if os.path.exists('dev-enabled'):
            self._developmentMode = True
            logger.set_level(logger.LEVEL_DEBUG)
            logger.warn('DEVELOPMENT MODE ENABLED (THIS IS LESS SECURE!)')
        else:
            self._developmentMode = False
            logger.set_level(logger.LEVEL_INFO)

        self.onionrCore = core.Core()
        self.onionrUtils = OnionrUtils(self.onionrCore)

        # Get configuration and Handle commands

        self.debug = False # Whole application debugging

        if os.path.exists('data-encrypted.dat'):
            while True:
                print('Enter password to decrypt:')
                password = getpass.getpass()
                result = self.onionrCore.dataDirDecrypt(password)
                if os.path.exists('data/'):
                    break
                else:
                    logger.error('Failed to decrypt: ' + result[1])
        else:
            if not os.path.exists('data/'):
                os.mkdir('data/')
                os.mkdir('data/blocks/')

        if not os.path.exists('data/peers.db'):
            self.onionrCore.createPeerDB()
            pass

        # Get configuration
        self.config = configparser.ConfigParser()
        if os.path.exists('data/config.ini'):
            self.config.read('data/config.ini')
        else:
            # Generate default config
            # Hostname should only be set if different from 127.x.x.x. Important for DNS rebinding attack prevention.
            if self.debug:
                randomPort = 8080
            else:
                while True:
                    randomPort = random.randint(1024, 65535)
                    if self.onionrUtils.checkPort(randomPort):
                        break
            self.config['CLIENT'] = {'CLIENT HMAC': base64.b64encode(os.urandom(32)).decode('utf-8'), 'PORT': randomPort, 'API VERSION': API_VERSION}
            with open('data/config.ini', 'w') as configfile:
                self.config.write(configfile)

        command = ''
        try:
            command = sys.argv[1].lower()
        except IndexError:
            command = ''
        finally:
            self.execute(command)

        if not self._developmentMode:
            encryptionPassword = self.onionrUtils.getPassword('Enter password to encrypt directory: ')
            self.onionrCore.dataDirEncrypt(encryptionPassword)
            shutil.rmtree('data/')

        return

    '''
        THIS SECTION HANDLES THE COMMANDS
    '''

    def getCommands(self):
        return {
            'start': self.start,
            'stop': self.killDaemon,
            'version': self.version,
            'listpeers': self.listPeers,
            'list-peers': self.listPeers,
            'stats': self.showStats,
            'help': self.showHelp,
            '': self.showHelpSuggestion,
            'addmsg': self.addMessage,
            'addmessage': self.addMessage,
            'add-msg': self.addMessage,
            'add-message': self.addMessage,
            'gui': self.openGUI,
            'addpeer': self.addPeer,
            'add-peer': self.addPeer
        }

    def execute(self, argument):
        argument = argument[argument.startswith('--') and len('--'):] # remove -- if it starts with it

        # define commands
        commands = self.getCommands()

        command = commands.get(argument, self.notFound)
        command()

    '''
        THIS SECTION DEFINES THE COMMANDS
    '''

    def version(self):
        logger.info('Onionr ' + ONIONR_VERSION + ' (' + platform.machine() + ') : API v' + API_VERSION)
        logger.info('Running on ' + platform.platform() + ' ' + platform.release())

    def openGUI(self):
        gui.OnionrGUI(self.onionrCore)

    def listPeers(self):
        logger.info('Peer list:\n')
        for i in self.onionrCore.listPeers():
            logger.info(i)

    def addPeer(self):
        try:
            newPeer = sys.argv[2]
        except:
            pass
        else:
            logger.info("Adding peer: " + logger.colors.underline + newPeer)
            self.onionrCore.addPeer(newPeer)

    def addMessage(self):
        while True:
            messageToAdd = '-txt-' + logger.readline('Broadcast message to network: ')
            if len(messageToAdd) >= 1:
                break
        addedHash = self.onionrCore.setData(messageToAdd)
        self.onionrCore.addToBlockDB(addedHash, selfInsert=True)
        self.onionrCore.setBlockType(addedHash, 'txt')

    def notFound(self):
        logger.error('Command not found.')

    def showHelpSuggestion(self):
        logger.info('Do ' + logger.colors.bold + sys.argv[0] + ' --help' + logger.colors.reset + logger.colors.fg.green + ' for Onionr help.')

    def start(self):
        if os.path.exists('.onionr-lock'):
            logger.fatal('Cannot start. Daemon is already running, or it did not exit cleanly.\n(if you are sure that there is not a daemon running, delete .onionr-lock & try again).')
        else:
            if not self.debug and not self._developmentMode:
                lockFile = open('.onionr-lock', 'w')
                lockFile.write('')
                lockFile.close()
            self.daemon()
            if not self.debug and not self._developmentMode:
                os.remove('.onionr-lock')

    def daemon(self):
        ''' Start the Onionr communication daemon '''
        if not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            net = NetController(self.config['CLIENT']['PORT'])
            logger.info('Tor is starting...')
            if not net.startTor():
                sys.exit(1)
            logger.info('Started Tor .onion service: ' + logger.colors.underline + net.myID)
            time.sleep(1)
            subprocess.Popen(["./communicator.py", "run", str(net.socksPort)])
            logger.debug('Started communicator')
        api.API(self.config, self.debug)

        return

    def killDaemon(self):
        ''' Shutdown the Onionr Daemon '''

        logger.warn('Killing the running daemon')
        net = NetController(self.config['CLIENT']['PORT'])
        try:
            self.onionrUtils.localCommand('shutdown')
        except requests.exceptions.ConnectionError:
            pass
        self.onionrCore.daemonQueueAdd('shutdown')
        net.killTor()

        return

    def showStats(self):
        ''' Display statistics and exit '''

        return

    def showHelp(self):
        ''' Show help for Onionr '''

        return

Onionr()
