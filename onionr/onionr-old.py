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
from etc import onionrvalues
if sys.version_info[0] == 2 or sys.version_info[1] < MIN_PY_VERSION:
    sys.stderr.write('Error, Onionr requires Python 3.%s+\n' % (MIN_PY_VERSION,))
    sys.exit(1)

from utils import detectoptimization
if detectoptimization.detect_optimization():
    sys.stderr.write('Error, Onionr cannot be run with an optimized Python interpreter\n')
    sys.exit(1)
from utils import createdirs
createdirs.create_dirs()
import os, base64, random, shutil, time, platform, signal
from threading import Thread
import config, logger, onionrplugins as plugins, onionrevents as events
import netcontroller
from onionrblockapi import Block
import onionrexceptions, communicator, setupconfig
import onionrcommands as commands # Many command definitions are here
from utils import identifyhome, hastor
from coredb import keydb
import filepaths

try:
    from urllib3.contrib.socks import SOCKSProxyManager
except ImportError:
    raise ImportError("You need the PySocks module (for use with socks5 proxy to use Tor)")

class Onionr:
    def __init__(self):
        '''
            Main Onionr class. This is for the CLI program, and does not handle much of the logic.
            In general, external programs and plugins should not use this class.
        '''
        self.API_VERSION = onionrvalues.API_VERSION
        self.userRunDir = os.getcwd() # Directory user runs the program from
        self.killed = False
        self.config = config

        if sys.argv[0] == os.path.basename(__file__):
            try:
                os.chdir(sys.path[0])
            except FileNotFoundError:
                pass

        # set data dir
        self.dataDir = identifyhome.identify_home()
        if not self.dataDir.endswith('/'):
            self.dataDir += '/'

        # Load global configuration data
        data_exists = Onionr.setupConfig(self)

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
                except Exception as e:
                    #logger.warn('Error enabling plugin: ' + str(e), terminal=True)
                    plugins.disable(name, onionr = self, stop_event = False)

        self.communicatorInst = None
        #self.deleteRunFiles()

        self.clientAPIInst = '' # Client http api instance
        self.publicAPIInst = '' # Public http api instance

        signal.signal(signal.SIGTERM, self.exitSigterm)

        # Handle commands

        self.debug = False # Whole application debugging

        # Get configuration
        if type(config.get('client.webpassword')) is type(None):
            config.set('client.webpassword', base64.b16encode(os.urandom(32)).decode('utf-8'), savefile=True)
        if type(config.get('client.client.port')) is type(None):
            randomPort = netcontroller.get_open_port()
            config.set('client.client.port', randomPort, savefile=True)
        if type(config.get('client.public.port')) is type(None):
            randomPort = netcontroller.get_open_port()
            config.set('client.public.port', randomPort, savefile=True)
        if type(config.get('client.api_version')) is type(None):
            config.set('client.api_version', onionrvalues.API_VERSION, savefile=True)

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
        
        os.chdir(self.userRunDir)
        return

    def exitSigterm(self, signum, frame):
        self.killed = True

    def doExport(self, bHash):
        exportDir = self.dataDir + 'block-export/'
        if not os.path.exists(exportDir):
            if os.path.exists(self.dataDir):
                os.mkdir(exportDir)
            else:
                logger.error('Onionr Not initialized')
        data = onionrstorage.getData(bHash)
        with open('%s/%s.dat' % (exportDir, bHash), 'wb') as exportFile:
            exportFile.write(data)

    def deleteRunFiles(self):
        try:
            os.remove(filepaths.public_API_host_file)
        except FileNotFoundError:
            pass
        try:
            os.remove(filepaths.private_API_host_file)
        except FileNotFoundError:
            pass

    '''
        Handle command line commands
    '''

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
        logger.info('Peer transport address list:', terminal=True)
        for i in keydb.listkeys.list_adders():
            logger.info(i, terminal=True)

    def getWebPassword(self):
        return config.get('client.webpassword')

    def printWebPassword(self):
        logger.info(self.getWebPassword(), terminal=True)

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
        
    def execute(self, argument):
        '''
            Executes a command
        '''

        argument = argument[argument.startswith('--') and len('--'):] # remove -- if it starts with it

        # define commands
        commands = self.getCommands()

        command = commands.get(argument, self.notFound)
        command()

    def listKeys(self):
        '''
            Displays a list of keys (used to be called peers) (?)
        '''
        logger.info('%sPublic keys in database: \n%s%s' % (logger.colors.fg.lightgreen, logger.colors.fg.green, '\n'.join(keydb.listkeys.list_peers()())), terminal=True)

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

        logger.error('Invalid command.', timestamp = False, terminal=True)

    def showHelpSuggestion(self):
        '''
            Displays a message suggesting help
        '''
        logger.info('Do ' + logger.colors.bold + sys.argv[0] + ' --help' + logger.colors.reset + logger.colors.fg.green + ' for Onionr help.', terminal=True)

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