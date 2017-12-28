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
import sys, os, threading, configparser, base64, random
import gui, api, colors
from colors import Colors

class Onionr:
    def __init__(self):
        colors = Colors()

        # Get configuration and Handle commands
        
        self.debug = True # Whole application debugging

        os.chdir(sys.path[0])

        if not os.path.exists('data'):
            os.mkdir('data')

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
            self.config['CLIENT'] = {'CLIENT HMAC': base64.b64encode(os.urandom(32)).decode('utf-8'), 'PORT': randomPort}
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
                return
        return
    def daemon(self):
        api.API(self.config, self.debug)
        return
    def killDaemon(self):
        return
    def showStats(self):
        return
    def showHelp(self):
        return

Onionr()
