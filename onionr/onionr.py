#!/usr/bin/env python3
'''
    Onionr - Private P2P Communication

    This file initializes Onionr when ran to be a daemon or with commands

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
import sys
MIN_PY_VERSION = 6
if sys.version_info[0] == 2 or sys.version_info[1] < MIN_PY_VERSION:
    sys.stderr.write('Error, Onionr requires Python 3.%s+' % (MIN_PY_VERSION,))
    sys.exit(1)
import os, base64, random, shutil, time, platform, signal
from threading import Thread
import api, core, config, logger, onionrplugins as plugins, onionrevents as events
import onionrutils
import netcontroller
from netcontroller import NetController
from onionrblockapi import Block
import onionrproofs, onionrexceptions, communicator, setupconfig
import onionrcommands as commands # Many command definitions are here

try:
    from urllib3.contrib.socks import SOCKSProxyManager
except ImportError:
    raise Exception("You need the PySocks module (for use with socks5 proxy to use Tor)")

ONIONR_TAGLINE = 'Private P2P Communication - GPLv3 - https://Onionr.net'
ONIONR_VERSION = '0.0.0' # for debugging and stuff
ONIONR_VERSION_TUPLE = tuple(ONIONR_VERSION.split('.')) # (MAJOR, MINOR, VERSION)
API_VERSION = '0' # increments of 1; only change when something fundamental about how the API works changes. This way other nodes know how to communicate without learning too much information about you.

class Onionr:
    def __init__(self):
        '''
            Main Onionr class. This is for the CLI program, and does not handle much of the logic.
            In general, external programs and plugins should not use this class.
        '''
        self.userRunDir = os.getcwd() # Directory user runs the program from
        self.killed = False

        if sys.argv[0] == os.path.basename(__file__):
            try:
                os.chdir(sys.path[0])
            except FileNotFoundError:
                pass

        # set data dir
        self.dataDir = os.environ.get('ONIONR_HOME', os.environ.get('DATA_DIR', 'data/'))
        if not self.dataDir.endswith('/'):
            self.dataDir += '/'

        # set log file
        logger.set_file(os.environ.get('LOG_DIR', 'data') + '/onionr.log')

        # Load global configuration data
        data_exists = Onionr.setupConfig(self.dataDir, self)

        if netcontroller.torBinary() is None:
            logger.error('Tor is not installed')
            sys.exit(1)

        # If block data folder does not exist
        if not os.path.exists(self.dataDir + 'blocks/'):
            os.mkdir(self.dataDir + 'blocks/')

        # Copy default plugins into plugins folder
        if not os.path.exists(plugins.get_plugins_folder()):
            if os.path.exists('static-data/default-plugins/'):
                names = [f for f in os.listdir("static-data/default-plugins/")]
                shutil.copytree('static-data/default-plugins/', plugins.get_plugins_folder())

                # Enable plugins
                for name in names:
                    if not name in plugins.get_enabled_plugins():
                        plugins.enable(name, self)

        for name in plugins.get_enabled_plugins():
            if not os.path.exists(plugins.get_plugin_data_folder(name)):
                try:
                    os.mkdir(plugins.get_plugin_data_folder(name))
                except:
                    plugins.disable(name, onionr = self, stop_event = False)

        self.communicatorInst = None
        self.onionrCore = core.Core()
        self.onionrCore.onionrInst = self
        #self.deleteRunFiles()
        self.onionrUtils = onionrutils.OnionrUtils(self.onionrCore)

        self.clientAPIInst = '' # Client http api instance
        self.publicAPIInst = '' # Public http api instance

        signal.signal(signal.SIGTERM, self.exitSigterm)

        # Handle commands

        self.debug = False # Whole application debugging

        # Get configuration
        if type(config.get('client.webpassword')) is type(None):
            config.set('client.webpassword', base64.b16encode(os.urandom(32)).decode('utf-8'), savefile=True)
        if type(config.get('client.client.port')) is type(None):
            randomPort = netcontroller.getOpenPort()
            config.set('client.client.port', randomPort, savefile=True)
        if type(config.get('client.public.port')) is type(None):
            randomPort = netcontroller.getOpenPort()
            config.set('client.public.port', randomPort, savefile=True)
        if type(config.get('client.participate')) is type(None):
            config.set('client.participate', True, savefile=True)
        if type(config.get('client.api_version')) is type(None):
            config.set('client.api_version', API_VERSION, savefile=True)

        self.cmds = commands.get_commands(self)
        self.cmdhelp = commands.cmd_help

        # initialize plugins
        events.event('init', onionr = self, threaded = False)

        command = ''
        try:
            command = sys.argv[1].lower()
        except IndexError:
            command = ''
        finally:
            self.execute(command)

        return

    def exitSigterm(self, signum, frame):
        self.killed = True

    def setupConfig(dataDir, self = None):
        return setupconfig.setup_config(dataDir, self)

    def cmdHeader(self):
        if len(sys.argv) >= 3:
            self.header(logger.colors.fg.pink + sys.argv[2].replace('Onionr', logger.colors.bold + 'Onionr' + logger.colors.reset + logger.colors.fg.pink))
        else:
            self.header(None)

    def header(self, message = logger.colors.fg.pink + logger.colors.bold + 'Onionr' + logger.colors.reset + logger.colors.fg.pink + ' has started.'):
        if os.path.exists('static-data/header.txt') and logger.get_level() <= logger.LEVEL_INFO:
            with open('static-data/header.txt', 'rb') as file:
                # only to stdout, not file or log or anything
                sys.stderr.write(file.read().decode().replace('P', logger.colors.fg.pink).replace('W', logger.colors.reset + logger.colors.bold).replace('G', logger.colors.fg.green).replace('\n', logger.colors.reset + '\n').replace('B', logger.colors.bold).replace('A', '%s' % API_VERSION).replace('V', ONIONR_VERSION))

                if not message is None:
                    logger.info(logger.colors.fg.lightgreen + '-> ' + str(message) + logger.colors.reset + logger.colors.fg.lightgreen + ' <-\n', sensitive=True)

    def deleteRunFiles(self):
        try:
            os.remove(self.onionrCore.publicApiHostFile)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.onionrCore.privateApiHostFile)
        except FileNotFoundError:
            pass

    def get_hostname(self):
        try:
            with open('./' + self.dataDir + 'hs/hostname', 'r') as hostname:
                return hostname.read().strip()
        except FileNotFoundError:
            return "Not Generated"
        except Exception:
            return None

    def getConsoleWidth(self):
        '''
            Returns an integer, the width of the terminal/cmd window
        '''

        columns = 80

        try:
            columns = int(os.popen('stty size', 'r').read().split()[1])
        except:
            # if it errors, it's probably windows, so default to 80.
            pass

        return columns

    '''
        Handle command line commands
    '''

    def exportBlock(self):
        commands.exportblocks(self)

    def showDetails(self):
        commands.onionrstatistics.show_details(self)

    def openHome(self):
        commands.openwebinterface.open_home(self)

    def addID(self):
        commands.pubkeymanager.add_ID(self)

    def changeID(self):
        commands.pubkeymanager.change_ID(self)

    def getCommands(self):
        return self.cmds

    def friendCmd(self):
        '''List, add, or remove friend(s)
        Changes their peer DB entry.
        '''
        commands.pubkeymanager.friend_command(self)

    def banBlock(self):
        commands.banblocks.ban_block(self)

    def listConn(self):
        commands.onionrstatistics.show_peers(self)

    def listPeers(self):
        logger.info('Peer transport address list:')
        for i in self.onionrCore.listAdders():
            logger.info(i)

    def getWebPassword(self):
        return config.get('client.webpassword')

    def printWebPassword(self):
        logger.info(self.getWebPassword(), sensitive = True)

    def getHelp(self):
        return self.cmdhelp

    def addCommand(self, command, function):
        self.cmds[str(command).lower()] = function

    def addHelp(self, command, description):
        self.cmdhelp[str(command).lower()] = str(description)

    def delCommand(self, command):
        return self.cmds.pop(str(command).lower(), None)

    def delHelp(self, command):
        return self.cmdhelp.pop(str(command).lower(), None)

    def configure(self):
        '''
            Displays something from the configuration file, or sets it
        '''

        if len(sys.argv) >= 4:
            config.reload()
            config.set(sys.argv[2], sys.argv[3], True)
            logger.debug('Configuration file updated.')
        elif len(sys.argv) >= 3:
            config.reload()
            logger.info(logger.colors.bold + sys.argv[2] + ': ' + logger.colors.reset + str(config.get(sys.argv[2], logger.colors.fg.red + 'Not set.')))
        else:
            logger.info(logger.colors.bold + 'Get a value: ' + logger.colors.reset + sys.argv[0] + ' ' + sys.argv[1] + ' <key>')
            logger.info(logger.colors.bold + 'Set a value: ' + logger.colors.reset + sys.argv[0] + ' ' + sys.argv[1] + ' <key> <value>')

    def execute(self, argument):
        '''
            Executes a command
        '''

        argument = argument[argument.startswith('--') and len('--'):] # remove -- if it starts with it

        # define commands
        commands = self.getCommands()

        command = commands.get(argument, self.notFound)
        command()

    def version(self, verbosity = 5, function = logger.info):
        '''
            Displays the Onionr version
        '''

        function('Onionr v%s (%s) (API v%s)' % (ONIONR_VERSION, platform.machine(), API_VERSION))
        if verbosity >= 1:
            function(ONIONR_TAGLINE)
        if verbosity >= 2:
            function('Running on %s %s' % (platform.platform(), platform.release()))

    def doPEX(self):
        '''make communicator do pex'''
        logger.info('Sending pex to command queue...')
        self.onionrCore.daemonQueueAdd('pex')

    def listKeys(self):
        '''
            Displays a list of keys (used to be called peers) (?)
        '''
        logger.info('%sPublic keys in database: \n%s%s' % (logger.colors.fg.lightgreen, logger.colors.fg.green, '\n'.join(self.onionrCore.listPeers())))

    def addPeer(self):
        '''
            Adds a peer (?)
        '''
        commands.keyadders.add_peer(self)

    def addAddress(self):
        '''
            Adds a Onionr node address
        '''
        commands.keyadders.add_address(self)

    def enablePlugin(self):
        '''
            Enables and starts the given plugin
        '''
        commands.plugincommands.enable_plugin(self)

    def disablePlugin(self):
        '''
            Disables and stops the given plugin
        '''
        commands.plugincommands.disable_plugin(self)

    def reloadPlugin(self):
        '''
            Reloads (stops and starts) all plugins, or the given plugin
        '''
        commands.plugincommands.reload_plugin(self)

    def createPlugin(self):
        '''
            Creates the directory structure for a plugin name
        '''
        commands.plugincommands.create_plugin(self)

    def notFound(self):
        '''
            Displays a "command not found" message
        '''

        logger.error('Command not found.', timestamp = False)

    def showHelpSuggestion(self):
        '''
            Displays a message suggesting help
        '''
        if __name__ == '__main__':
            logger.info('Do ' + logger.colors.bold + sys.argv[0] + ' --help' + logger.colors.reset + logger.colors.fg.green + ' for Onionr help.')

    def start(self, input = False, override = False):
        '''
            Starts the Onionr daemon
        '''
        if config.get('general.dev_mode', False):
            override = True
        commands.daemonlaunch.start(self, input, override)

    def setClientAPIInst(self, inst):
        self.clientAPIInst = inst

    def getClientApi(self):
        while self.clientAPIInst == '':
            time.sleep(0.5)
        return self.clientAPIInst

    def daemon(self):
        '''
            Starts the Onionr communication daemon
        '''
        commands.daemonlaunch.daemon(self)

    def killDaemon(self):
        '''
            Shutdown the Onionr daemon
        '''
        commands.daemonlaunch.kill_daemon(self)

    def showStats(self):
        '''
            Displays statistics and exits
        '''
        commands.onionrstatistics.show_stats(self)

    def showHelp(self, command = None):
        '''
            Show help for Onionr
        '''
        commands.show_help(self, command)

    def getFile(self):
        '''
            Get a file from onionr blocks
        '''
        commands.filecommands.getFile(self)

    def addWebpage(self):
        '''
            Add a webpage to the onionr network
        '''
        self.addFile(singleBlock=True, blockType='html')

    def addFile(self, singleBlock=False, blockType='bin'):
        '''
            Adds a file to the onionr network
        '''
        commands.filecommands.add_file(self, singleBlock, blockType)

if __name__ == "__main__":
    Onionr()
