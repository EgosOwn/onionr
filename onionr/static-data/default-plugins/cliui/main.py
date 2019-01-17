'''
    Onionr - P2P Anonymous Storage Network

    This is an interactive menu-driven CLI interface for Onionr
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

# Imports some useful libraries
import logger, config, threading, time, uuid, subprocess, sys
from onionrblockapi import Block

plugin_name = 'cliui'
PLUGIN_VERSION = '0.0.1'

class OnionrCLIUI:
    def __init__(self, apiInst):
        self.api = apiInst
        self.myCore = apiInst.get_core()
        return

    def subCommand(self, command, args=None):
            try:
                #subprocess.run(["./onionr.py", command])
                #subprocess.Popen(['./onionr.py', command], stdin=subprocess.STD, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT)
                if args != None:
                    subprocess.call(['./onionr.py', command, args])
                else:
                    subprocess.call(['./onionr.py', command])
            except KeyboardInterrupt:
                pass

    def refresh(self):
            print('\n' * 80 + logger.colors.reset)

    def start(self):
        '''Main CLI UI interface menu'''
        showMenu = True
        isOnline = 'No'
        firstRun = True
        choice = ''
        if self.myCore._utils.localCommand('ping', maxWait=10) == 'pong!':
            firstRun = False

        while showMenu:
            if self.myCore._utils.localCommand('ping', maxWait=2) == 'pong!':
                isOnline = "Yes"
            else:
                isOnline = "No"

            print('''Daemon Running: ''' + isOnline + '''
1. Flow (Anonymous public chat, use at your own risk)
2. Mail (Secure email-like service)
3. File Sharing
4. Quit (Does not shutdown daemon)
            ''')
            try:
                choice = input(">").strip().lower()
            except (KeyboardInterrupt, EOFError):
                choice = "quit"

            if choice in ("flow", "1"):
                self.subCommand("flow")
            elif choice in ("2", "mail"):
                self.subCommand("mail")
            elif choice in ("3", "file sharing", "file"):
                filename = input("Enter full path to file: ").strip()
                self.subCommand("addfile", filename)
            elif choice in ("4", "quit"):
                showMenu = False
            elif choice == "":
                pass
            else:
                logger.error("Invalid choice")
        return


def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    # Doing this makes it so that the other functions can access the api object
    # by simply referencing the variable `pluginapi`.
    pluginapi = api
    ui = OnionrCLIUI(api)
    api.commands.register('interactive', ui.start)
    api.commands.register_help('interactive', 'Open the CLI interface')
    return
