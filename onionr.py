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
import sys, os, configparser, base64, random, getpass, shutil, subprocess
import gui, api, colors, core
from onionrutils import OnionrUtils
from colors import Colors

class Onionr:
    def __init__(self):
        '''Main Onionr class. This is for the CLI program, and does not handle much of the logic.
        In general, external programs and plugins should not use this class.

        '''
        if os.path.exists('dev-enabled'):
            print('DEVELOPMENT MODE ENABLED (THIS IS LESS SECURE!)')
            self._developmentMode = True
        else:
            self._developmentMode = False

        colors = Colors()

        onionrCore = core.Core()
        onionrUtils = OnionrUtils()

        # Get configuration and Handle commands
        
        self.debug = False # Whole application debugging
        try:
            os.chdir(sys.path[0])
        except FileNotFoundError:
            pass

        if os.path.exists('data-encrypted.dat'):
            while True:
                print('Enter password to decrypt:')
                password = getpass.getpass()
                result = onionrCore.dataDirDecrypt(password)
                if os.path.exists('data/'):
                    break
                else:
                    print('Failed to decrypt: ' + result[1])
        else:
            if not os.path.exists('data/'):
                os.mkdir('data/')
        
        if not os.path.exists('data/peers.db'):
            onionrCore.createPeerDB()
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
                randomPort = random.randint(1024, 65535)
            self.config['CLIENT'] = {'CLIENT HMAC': base64.b64encode(os.urandom(32)).decode('utf-8'), 'PORT': randomPort, 'API VERSION': '0.0.0'}
            with open('data/config.ini', 'w') as configfile:
                self.config.write(configfile)
        command = ''
        try:
            command = sys.argv[1].lower()
        except IndexError:
            command = ''
        finally:
            if command == 'start':
                self.daemon()
            elif command == 'stop':
                self.killDaemon()
            elif command == 'stats':
                self.showStats()
            elif command == 'help' or command == '--help':
                self.showHelp()
            elif command == '':
                print('Do', sys.argv[0], ' --help for Onionr help.')
            else:
                print(colors.RED, 'Invalid Command', colors.RESET)
                
        if not self._developmentMode:
            encryptionPassword = onionrUtils.getPassword('Enter password to encrypt directory.')
            onionrCore.dataDirEncrypt(encryptionPassword)
            shutil.rmtree('data/')
        return
    def daemon(self):
        if not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            subprocess.Popen(["./communicator.py", "run"])
            print('Started communicator')
        api.API(self.config, self.debug)
        return
    def killDaemon(self):
        return
    def showStats(self):
        return
    def showHelp(self):
        return

Onionr()