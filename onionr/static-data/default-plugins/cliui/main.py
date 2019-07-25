'''
    Onionr - Private P2P Communication

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
import threading, time, uuid, subprocess, sys
import config, logger
from onionrblockapi import Block
import onionrplugins
from onionrutils import localcommand

plugin_name = 'cliui'
PLUGIN_VERSION = '0.0.1'

class OnionrCLIUI:
    def __init__(self, apiInst):
        self.api = apiInst
        self.shutdown = False
        self.running = 'undetermined'
        enabled = onionrplugins.get_enabled_plugins()
        self.mail_enabled = 'pms' in enabled
        self.flow_enabled = 'flow' in enabled

    def subCommand(self, command, args=None):
            try:
                if args != None:
                    subprocess.call(['./onionr.py', command, args])
                else:
                    subprocess.call(['./onionr.py', command])
            except KeyboardInterrupt:
                pass
    
    def isRunning(self):
        while not self.shutdown:
            if localcommand.local_command('ping', maxWait=5) == 'pong!':
                self.running = 'Yes'
            else:
                self.running = 'No'
            time.sleep(5)

    def refresh(self):
            print('\n' * 80 + logger.colors.reset)

    def start(self):
        '''Main CLI UI interface menu'''
        showMenu = True
        choice = ''
        threading.Thread(target=self.isRunning).start()

        while showMenu:
            print('Onionr\n------')
            print('''Daemon Running: ''' + self.running + '''
1. Flow (Anonymous public shout box, use at your own risk)
2. Mail (Secure email-like service)
3. File Sharing
4. Quit (Does not shutdown daemon)
            ''')
            try:
                choice = input(">").strip().lower()
            except (KeyboardInterrupt, EOFError):
                choice = "quit"

            if choice in ("flow", "1"):
                if self.flow_enabled:
                    self.subCommand("flow")
                else:
                    logger.warn('flow plugin is not enabled')
            elif choice in ("2", "mail"):
                if self.mail_enabled:
                    self.subCommand("mail")
                else:
                    logger.warn('mail plugin not enabled')
            elif choice in ("3", "file sharing", "file"):
                try:
                    filename = input("Enter full path to file: ").strip()
                except (EOFError, KeyboardInterrupt) as e:
                    pass
                else:
                    if len(filename.strip()) > 0:
                        self.subCommand("addfile", filename)
            elif choice in ("4", "quit"):
                showMenu = False
                self.shutdown = True
            elif choice == "":
                pass
            else:
                logger.error("Invalid choice", terminal=True)
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
