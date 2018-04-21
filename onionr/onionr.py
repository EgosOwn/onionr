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
import sys, os, base64, random, getpass, shutil, subprocess, requests, time, platform
import api, core, config, logger, onionrplugins as plugins
from onionrutils import OnionrUtils
from netcontroller import NetController

try:
    from urllib3.contrib.socks import SOCKSProxyManager
except ImportError:
    raise Exception("You need the PySocks module (for use with socks5 proxy to use Tor)")

try:
    import gui
except ImportError:
    logger.error('You need python3 tkinter and tk installed to use Onionr.')
    sys.exit(1)

ONIONR_TAGLINE = 'Anonymous P2P Platform - GPLv3 - https://Onionr.VoidNet.Tech'
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

        # Load global configuration data

        exists = os.path.exists(config.get_config_file())
        config.set_config({'devmode': True, 'log': {'file': {'output': True, 'path': 'data/output.log'}, 'console': {'output': True, 'color': True}}}) # this is the default config, it will be overwritten if a config file already exists. Else, it saves it
        config.reload() # this will read the configuration file into memory

        settings = 0b000
        if config.get('log', {'console': {'color': True}})['console']['color']:
            settings = settings | logger.USE_ANSI
        if config.get('log', {'console': {'output': True}})['console']['output']:
            settings = settings | logger.OUTPUT_TO_CONSOLE
        if config.get('log', {'file': {'output': True}})['file']['output']:
            settings = settings | logger.OUTPUT_TO_FILE
            logger.set_file(config.get('log', {'file': {'path': 'data/output.log'}})['file']['path'])
        logger.set_settings(settings)

        if str(config.get('devmode', True)).lower() == 'true':
            self._developmentMode = True
            logger.set_level(logger.LEVEL_DEBUG)
        else:
            self._developmentMode = False
            logger.set_level(logger.LEVEL_INFO)
        print('enabled? ' + str(self._developmentMode))

        self.onionrCore = core.Core()
        self.onionrUtils = OnionrUtils(self.onionrCore)

        # Handle commands

        self.debug = False # Whole application debugging

        if os.path.exists('data-encrypted.dat'):
            while True:
                print('Enter password to decrypt:')
                password = getpass.getpass()
                result = self.onionrCore.dataDirDecrypt(password)
                if os.path.exists('data/'):
                    break
                else:
                    logger.error('Failed to decrypt: ' + result[1], timestamp = False)
        else:
            if not os.path.exists('data/'):
                os.mkdir('data/')
                os.mkdir('data/blocks/')

        if not os.path.exists(self.onionrCore.peerDB):
            self.onionrCore.createPeerDB()
            pass
        if not os.path.exists(self.onionrCore.addressDB):
            self.onionrCore.createAddressDB()

        # Get configuration

        if not exists:
            # Generate default config
            # Hostname should only be set if different from 127.x.x.x. Important for DNS rebinding attack prevention.
            if self.debug:
                randomPort = 8080
            else:
                while True:
                    randomPort = random.randint(1024, 65535)
                    if self.onionrUtils.checkPort(randomPort):
                        break
            config.set('client', {'participate': 'true', 'client_hmac': base64.b16encode(os.urandom(32)).decode('utf-8'), 'port': randomPort, 'api_version': API_VERSION}, True)

        self.cmds = {
            '': self.showHelpSuggestion,
            'help': self.showHelp,
            'version': self.version,
            'config': self.configure,
            'start': self.start,
            'stop': self.killDaemon,
            'stats': self.showStats,

            'enable-plugin': self.enablePlugin,
            'enplugin': self.enablePlugin,
            'enableplugin': self.enablePlugin,
            'enmod': self.enablePlugin,
            'disable-plugin': self.disablePlugin,
            'displugin': self.disablePlugin,
            'disableplugin': self.disablePlugin,
            'dismod': self.disablePlugin,
            'reload-plugin': self.reloadPlugin,
            'reloadplugin': self.reloadPlugin,
            'reload-plugins': self.reloadPlugin,
            'reloadplugins': self.reloadPlugin,

            'listkeys': self.listKeys,
            'list-keys': self.listKeys,

            'addmsg': self.addMessage,
            'addmessage': self.addMessage,
            'add-msg': self.addMessage,
            'add-message': self.addMessage,
            'pm': self.sendEncrypt,

            'getpms': self.getPMs,
            'get-pms': self.getPMs,

            'gui': self.openGUI,

            'addpeer': self.addPeer,
            'add-peer': self.addPeer,
            'add-address': self.addAddress,
            'add-addr': self.addAddress,
            'addaddr': self.addAddress,
            'addaddress': self.addAddress,

            'connect': self.addAddress
        }

        self.cmdhelp = {
            'help': 'Displays this Onionr help menu',
            'version': 'Displays the Onionr version',
            'config': 'Configures something and adds it to the file',
            'start': 'Starts the Onionr daemon',
            'stop': 'Stops the Onionr daemon',
            'stats': 'Displays node statistics',
            'enable-plugin': 'Enables and starts a plugin',
            'disable-plugin': 'Disables and stops a plugin',
            'reload-plugin': 'Reloads a plugin',
            'add-peer': 'Adds a peer (?)',
            'list-peers': 'Displays a list of peers',
            'add-msg': 'Broadcasts a message to the Onionr network',
            'pm': 'Adds a private message to block',
            'get-pms': 'Shows private messages sent to you',
            'gui': 'Opens a graphical interface for Onionr'
        }

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
        return self.cmds

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
        
        return

    '''
        THIS SECTION DEFINES THE COMMANDS
    '''

    def version(self, verbosity=5):
        '''
            Displays the Onionr version
        '''
        logger.info('Onionr ' + ONIONR_VERSION + ' (' + platform.machine() + ') - API v' + API_VERSION)
        if verbosity >= 1:
            logger.info(ONIONR_TAGLINE)
        if verbosity >= 2:
            logger.info('Running on ' + platform.platform() + ' ' + platform.release())
            
        return

    def sendEncrypt(self):
        '''
            Create a private message and send it
        '''
        invalidID = True
        while invalidID:
            try:
                peer = logger.readline('Peer to send to: ')
            except KeyboardInterrupt:
                break
            else:
                if self.onionrUtils.validatePubKey(peer):
                    invalidID = False
                else:
                    logger.error('Invalid peer ID')
        else:
            try:
                message = logger.readline("Enter a message: ")
            except KeyboardInterrupt:
                pass
            else:
                logger.info("Sending message to " + peer)
                self.onionrUtils.sendPM(peer, message)


    def openGUI(self):
        '''
            Opens a graphical interface for Onionr
        '''

        gui.OnionrGUI(self.onionrCore)

    def listKeys(self):
        '''
            Displays a list of keys (used to be called peers) (?)
        '''

        logger.info('Public keys in database:\n')
        for i in self.onionrCore.listPeers():
            logger.info(i)

    def addPeer(self):
        '''
            Adds a peer (?)
        '''

        try:
            newPeer = sys.argv[2]
        except:
            pass
        else:
            logger.info("Adding peer: " + logger.colors.underline + newPeer)
            self.onionrCore.addPeer(newPeer)

        return

    def addAddress(self):
        '''
            Adds a Onionr node address
        '''
        try:
            newAddress = sys.argv[2]
        except:
            pass
        else:
            logger.info("Adding address: " + logger.colors.underline + newAddress)
            if self.onionrCore.addAddress(newAddress):
                logger.info("Successfully added address.")
            else:
                logger.warn("Unable to add address.")

        return

    def addMessage(self, header="txt"):
        '''
            Broadcasts a message to the Onionr network
        '''

        while True:

            messageToAdd = '-txt-' + logger.readline('Broadcast message to network: ')
            if len(messageToAdd) - 5 >= 1:
                break

        addedHash = self.onionrCore.setData(messageToAdd)
        self.onionrCore.addToBlockDB(addedHash, selfInsert=True)
        self.onionrCore.setBlockType(addedHash, 'txt')

        return

    def getPMs(self):
        '''
            display PMs sent to us
        '''
        self.onionrUtils.loadPMs()

    def enablePlugin(self):
        '''
            Enables and starts the given plugin
        '''

        if len(sys.argv) >= 3:
            plugin_name = sys.argv[2]
            logger.info('Enabling plugin \"' + plugin_name + '\"...')
            plugins.enable(plugin_name, self)
        else:
            logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' <plugin>')

        return

    def disablePlugin(self):
        '''
            Disables and stops the given plugin
        '''

        if len(sys.argv) >= 3:
            plugin_name = sys.argv[2]
            logger.info('Disabling plugin \"' + plugin_name + '\"...')
            plugins.disable(plugin_name, self)
        else:
            logger.info(sys.argv[0] + ' ' + sys.argv[1] + ' <plugin>')

        return

    def reloadPlugin(self):
        '''
            Reloads (stops and starts) all plugins, or the given plugin
        '''

        if len(sys.argv) >= 3:
            plugin_name = sys.argv[2]
            logger.info('Reloading plugin \"' + plugin_name + '\"...')
            plugins.stop(plugin_name, self)
            plugins.start(plugin_name, self)
        else:
            logger.info('Reloading all plugins...')
            plugins.reload(self)

        return

    def notFound(self):
        '''
            Displays a "command not found" message
        '''

        logger.error('Command not found.', timestamp = False)

    def showHelpSuggestion(self):
        '''
            Displays a message suggesting help
        '''

        logger.info('Do ' + logger.colors.bold + sys.argv[0] + ' --help' + logger.colors.reset + logger.colors.fg.green + ' for Onionr help.')

    def start(self):
        '''
            Starts the Onionr daemon
        '''

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
        '''
            Starts the Onionr communication daemon
        '''

        if not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            if self._developmentMode:
                logger.warn('DEVELOPMENT MODE ENABLED (THIS IS LESS SECURE!)')
            net = NetController(config.get('client')['port'])
            logger.info('Tor is starting...')
            if not net.startTor():
                sys.exit(1)
            logger.info('Started Tor .onion service: ' + logger.colors.underline + net.myID)
            logger.info('Our Public key: ' + self.onionrCore._crypto.pubKey)
            time.sleep(1)
            subprocess.Popen(["./communicator.py", "run", str(net.socksPort)])
            logger.debug('Started communicator')
        api.API(self.debug)

        return

    def killDaemon(self):
        '''
            Shutdown the Onionr daemon
        '''

        logger.warn('Killing the running daemon')
        net = NetController(config.get('client')['port'])
        try:
            self.onionrUtils.localCommand('shutdown')
        except requests.exceptions.ConnectionError:
            pass
        self.onionrCore.daemonQueueAdd('shutdown')
        net.killTor()

        return

    def showStats(self):
        '''
            Displays statistics and exits
        '''

        return

    def showHelp(self, command = None):
        '''
            Show help for Onionr
        '''

        helpmenu = self.getHelp()

        if command is None and len(sys.argv) >= 3:
            for cmd in sys.argv[2:]:
                self.showHelp(cmd)
        elif not command is None:
            if command.lower() in helpmenu:
                logger.info(logger.colors.bold + command  + logger.colors.reset + logger.colors.fg.blue + ' : ' + logger.colors.reset +  helpmenu[command.lower()])
            else:
                logger.warn(logger.colors.bold + command  + logger.colors.reset + logger.colors.fg.blue + ' : ' + logger.colors.reset + 'No help menu entry was found')
        else:
            self.version(0)
            for command, helpmessage in helpmenu.items():
                self.showHelp(command)
        return

Onionr()
