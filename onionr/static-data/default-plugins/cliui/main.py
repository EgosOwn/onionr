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
import logger, config, threading, time, uuid, subprocess
from onionrblockapi import Block

plugin_name = 'cliui'
PLUGIN_VERSION = '0.0.1'

class OnionrCLIUI:
    def __init__(self, apiInst):
        self.api = apiInst
        self.myCore = apiInst.get_core()
        return

    def subCommand(self, command):
            try:
                subprocess.run(["./onionr.py", command])
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

        if self.myCore._utils.localCommand('ping') == 'pong':
            firstRun = False

        while showMenu:
            if firstRun:
                logger.info('Please wait while Onionr starts...'')
                daemon = subprocess.Popen(["./onionr.py", "start"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
                time.sleep(30)
                firstRun = False

            if self.myCore._utils.localCommand('ping') == 'pong':
                isOnline = "Yes"
            else:
                isOnline = "No"

            logger.info('''Daemon Running: ''' + isOnline + '''

1. Flow (Anonymous public chat, use at your own risk)
2. Mail (Secure email-like service)
3. File Sharing
4. User Settings
5. Start/Stop Daemon
6. Quit (Does not shutdown daemon)
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
                logger.warn("Not supported yet")
            elif choice in ("4", "user settings", "settings"):
                try:
                    self.setName()
                except (KeyboardInterrupt, EOFError) as e:
                    pass
            elif choice in ("5", "daemon"):
                if isOnline == "Yes":
                    logger.info("Onionr daemon will shutdown...")
                    self.myCore.daemonQueueAdd('shutdown')
                    try:
                        daemon.kill()
                    except UnboundLocalError:
                        pass
                else:
                    logger.info("Starting Daemon...")
                    daemon = subprocess.Popen(["./onionr.py", "start"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            elif choice in ("6", "quit"):
                showMenu = False
            elif choice == "":
                pass
            else:
                logger.error("Invalid choice")
        return

    def setName(self):
        try:
            name = input("Enter your name: ")
            if name != "":
                self.myCore.insertBlock("userInfo-" + str(uuid.uuid1()), sign=True, header='userInfo', meta={'name': name})
        except KeyboardInterrupt:
            pass
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
