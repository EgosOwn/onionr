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

import sys
if sys.version_info[0] == 2 or sys.version_info[1] < 5:
    print('Error, Onionr requires Python 3.4+')
    sys.exit(1)
import os, base64, random, getpass, shutil, subprocess, requests, time, platform, datetime, re, json, getpass, sqlite3
from threading import Thread
import api, core, config, logger, onionrplugins as plugins, onionrevents as events
import onionrutils
from onionrutils import OnionrUtils
from netcontroller import NetController
from onionrblockapi import Block
import onionrproofs

try:
    from urllib3.contrib.socks import SOCKSProxyManager
except ImportError:
    raise Exception("You need the PySocks module (for use with socks5 proxy to use Tor)")

ONIONR_TAGLINE = 'Anonymous P2P Platform - GPLv3 - https://Onionr.VoidNet.Tech'
ONIONR_VERSION = '0.1.1' # for debugging and stuff
ONIONR_VERSION_TUPLE = tuple(ONIONR_VERSION.split('.')) # (MAJOR, MINOR, VERSION)
API_VERSION = '4' # increments of 1; only change when something fundemental about how the API works changes. This way other nodes know how to communicate without learning too much information about you.

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

        data_exists = os.path.exists('data/')

        if not data_exists:
            os.mkdir('data/')

        if os.path.exists('static-data/default_config.json'):
            config.set_config(json.loads(open('static-data/default_config.json').read())) # this is the default config, it will be overwritten if a config file already exists. Else, it saves it
        else:
            # the default config file doesn't exist, try hardcoded config
            config.set_config({'dev_mode': True, 'log': {'file': {'output': True, 'path': 'data/output.log'}, 'console': {'output': True, 'color': True}}})
        if not data_exists:
            config.save()
        config.reload() # this will read the configuration file into memory

        settings = 0b000
        if config.get('log.console.color', True):
            settings = settings | logger.USE_ANSI
        if config.get('log.console.output', True):
            settings = settings | logger.OUTPUT_TO_CONSOLE
        if config.get('log.file.output', True):
            settings = settings | logger.OUTPUT_TO_FILE
            logger.set_file(config.get('log.file.path', '/tmp/onionr.log'))
        logger.set_settings(settings)

        if str(config.get('general.dev_mode', True)).lower() == 'true':
            self._developmentMode = True
            logger.set_level(logger.LEVEL_DEBUG)
        else:
            self._developmentMode = False
            logger.set_level(logger.LEVEL_INFO)

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
            # If data folder does not exist
            if not data_exists:
                if not os.path.exists('data/blocks/'):
                    os.mkdir('data/blocks/')

            # Copy default plugins into plugins folder
            if not os.path.exists(plugins.get_plugins_folder()):
                if os.path.exists('static-data/default-plugins/'):
                    names = [f for f in os.listdir("static-data/default-plugins/") if not os.path.isfile(f)]
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

        if not os.path.exists(self.onionrCore.peerDB):
            self.onionrCore.createPeerDB()
            pass
        if not os.path.exists(self.onionrCore.addressDB):
            self.onionrCore.createAddressDB()

        # Get configuration
        if type(config.get('client.hmac')) is type(None):
            config.set('client.hmac', base64.b16encode(os.urandom(32)).decode('utf-8'), savefile=True)
        if type(config.get('client.port')) is type(None):
            #while True:
            randomPort = random.randint(1024, 65535)
            #    if self.onionrUtils.checkPort(randomPort):
            #        break
            config.set('client.port', randomPort, savefile=True)
        if type(config.get('client.participate')) is type(None):
            config.set('client.participate', True, savefile=True)
        if type(config.get('client.api_version')) is type(None):
            config.set('client.api_version', API_VERSION, savefile=True)
    

        self.cmds = {
            '': self.showHelpSuggestion,
            'help': self.showHelp,
            'version': self.version,
            'config': self.configure,
            'start': self.start,
            'stop': self.killDaemon,
            'status': self.showStats,
            'statistics': self.showStats,
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
            'create-plugin': self.createPlugin,
            'createplugin': self.createPlugin,
            'plugin-create': self.createPlugin,

            'listkeys': self.listKeys,
            'list-keys': self.listKeys,

            'addpeer': self.addPeer,
            'add-peer': self.addPeer,
            'add-address': self.addAddress,
            'add-addr': self.addAddress,
            'addaddr': self.addAddress,
            'addaddress': self.addAddress,
            'list-peers': self.listPeers,

            'add-file': self.addFile,
            'addfile': self.addFile,
            'listconn': self.listConn,

            'import-blocks': self.onionrUtils.importNewBlocks,
            'importblocks': self.onionrUtils.importNewBlocks,

            'introduce': self.onionrCore.introduceNode,
            'connect': self.addAddress,
            'kex': self.doKEX,
            'pex': self.doPEX,

            'ui' : self.openUI,
            'gui' : self.openUI,

            'getpassword': self.printWebPassword,
            'get-password': self.printWebPassword,
            'getpwd': self.printWebPassword,
            'get-pwd': self.printWebPassword,
            'getpass': self.printWebPassword,
            'get-pass': self.printWebPassword,
            'getpasswd': self.printWebPassword,
            'get-passwd': self.printWebPassword
        }

        self.cmdhelp = {
            'help': 'Displays this Onionr help menu',
            'version': 'Displays the Onionr version',
            'config': 'Configures something and adds it to the file',
            'start': 'Starts the Onionr daemon',
            'stop': 'Stops the Onionr daemon',
            'stats': 'Displays node statistics',
            'get-password': 'Displays the web password',
            'enable-plugin': 'Enables and starts a plugin',
            'disable-plugin': 'Disables and stops a plugin',
            'reload-plugin': 'Reloads a plugin',
            'create-plugin': 'Creates directory structure for a plugin',
            'add-peer': 'Adds a peer to database',
            'list-peers': 'Displays a list of peers',
            'add-file': 'Create an Onionr block from a file',
            'import-blocks': 'import blocks from the disk (Onionr is transport-agnostic!)',
            'listconn': 'list connected peers',
            'kex': 'exchange keys with peers (done automatically)',
            'pex': 'exchange addresses with peers (done automatically)',
            'introduce': 'Introduce your node to the public Onionr network',
        }

        # initialize plugins
        events.event('init', onionr = self, threaded = False)

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

    def listConn(self):
        self.onionrCore.daemonQueueAdd('connectedPeers')

    def listPeers(self):
        logger.info('Peer transport address list:')
        for i in self.onionrCore.listAdders():
            logger.info(i)

    def getWebPassword(self):
        return config.get('client.hmac')

    def printWebPassword(self):
        print(self.getWebPassword())

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

        logger.info('Onionr %s (%s) - API v%s' % (ONIONR_VERSION, platform.machine(), API_VERSION))
        if verbosity >= 1:
            logger.info(ONIONR_TAGLINE)
        if verbosity >= 2:
            logger.info('Running on %s %s' % (platform.platform(), platform.release()))

        return

    def doKEX(self):
        '''make communicator do kex'''
        logger.info('Sending kex to command queue...')
        self.onionrCore.daemonQueueAdd('kex')

    def doPEX(self):
        '''make communicator do pex'''
        logger.info('Sending pex to command queue...')
        self.onionrCore.daemonQueueAdd('pex')

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
            if self.onionrUtils.hasKey(newPeer):
                logger.info('We already have that key')
                return
            if not '-' in newPeer:
                logger.info('Since no POW token was supplied for that key, one is being generated')
                proof = onionrproofs.DataPOW(newPeer)
                while True:
                    result = proof.getResult()
                    if result == False:
                        time.sleep(0.5)
                    else:
                        break
                newPeer += '-' + base64.b64encode(result[1]).decode()
                logger.info(newPeer)

            logger.info("Adding peer: " + logger.colors.underline + newPeer)
            if self.onionrUtils.mergeKeys(newPeer):
                logger.info('Successfully added key')
            else:
                logger.error('Failed to add key')

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
            try:
                messageToAdd = logger.readline('Broadcast message to network: ')
                if len(messageToAdd) >= 1:
                    break
            except KeyboardInterrupt:
                return

        #addedHash = Block(type = 'txt', content = messageToAdd).save()
        addedHash = self.onionrCore.insertBlock(messageToAdd)
        if addedHash != None and addedHash != False and addedHash != "":
            logger.info("Message inserted as as block %s" % addedHash)
        else:
            logger.error('Failed to insert block.', timestamp = False)
        return

    def enablePlugin(self):
        '''
            Enables and starts the given plugin
        '''

        if len(sys.argv) >= 3:
            plugin_name = sys.argv[2]
            logger.info('Enabling plugin "%s"...' % plugin_name)
            plugins.enable(plugin_name, self)
        else:
            logger.info('%s %s <plugin>' % (sys.argv[0], sys.argv[1]))

        return

    def disablePlugin(self):
        '''
            Disables and stops the given plugin
        '''

        if len(sys.argv) >= 3:
            plugin_name = sys.argv[2]
            logger.info('Disabling plugin "%s"...' % plugin_name)
            plugins.disable(plugin_name, self)
        else:
            logger.info('%s %s <plugin>' % (sys.argv[0], sys.argv[1]))

        return

    def reloadPlugin(self):
        '''
            Reloads (stops and starts) all plugins, or the given plugin
        '''

        if len(sys.argv) >= 3:
            plugin_name = sys.argv[2]
            logger.info('Reloading plugin "%s"...' % plugin_name)
            plugins.stop(plugin_name, self)
            plugins.start(plugin_name, self)
        else:
            logger.info('Reloading all plugins...')
            plugins.reload(self)

        return

    def createPlugin(self):
        '''
            Creates the directory structure for a plugin name
        '''

        if len(sys.argv) >= 3:
            try:
                plugin_name = re.sub('[^0-9a-zA-Z]+', '', str(sys.argv[2]).lower())

                if not plugins.exists(plugin_name):
                    logger.info('Creating plugin "%s"...' % plugin_name)

                    os.makedirs(plugins.get_plugins_folder(plugin_name))
                    with open(plugins.get_plugins_folder(plugin_name) + '/main.py', 'a') as main:
                        contents = ''
                        with open('static-data/default_plugin.py', 'rb') as file:
                            contents = file.read().decode()

                        # TODO: Fix $user. os.getlogin() is   B U G G Y
                        main.write(contents.replace('$user', 'some random developer').replace('$date', datetime.datetime.now().strftime('%Y-%m-%d')).replace('$name', plugin_name))

                    with open(plugins.get_plugins_folder(plugin_name) + '/info.json', 'a') as main:
                        main.write(json.dumps({'author' : 'anonymous', 'description' : 'the default description of the plugin', 'version' : '1.0'}))

                    logger.info('Enabling plugin "%s"...' % plugin_name)
                    plugins.enable(plugin_name, self)
                else:
                    logger.warn('Cannot create plugin directory structure; plugin "%s" exists.' % plugin_name)

            except Exception as e:
                logger.error('Failed to create plugin directory structure.', e)
        else:
            logger.info('%s %s <plugin>' % (sys.argv[0], sys.argv[1]))

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

    def start(self, input = False, override = False):
        '''
            Starts the Onionr daemon
        '''

        if os.path.exists('.onionr-lock') and not override:
            logger.fatal('Cannot start. Daemon is already running, or it did not exit cleanly.\n(if you are sure that there is not a daemon running, delete .onionr-lock & try again).')
        else:
            if not self.debug and not self._developmentMode:
                lockFile = open('.onionr-lock', 'w')
                lockFile.write('')
                lockFile.close()
            self.running = True
            self.daemon()
            self.running = False
            if not self.debug and not self._developmentMode:
                os.remove('.onionr-lock')

    def daemon(self):
        '''
            Starts the Onionr communication daemon
        '''
        communicatorDaemon = './communicator2.py'
        if not os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            if self._developmentMode:
                logger.warn('DEVELOPMENT MODE ENABLED (THIS IS LESS SECURE!)', timestamp = False)
            net = NetController(config.get('client.port', 59496))
            logger.info('Tor is starting...')
            if not net.startTor():
                sys.exit(1)
            logger.info('Started .onion service: ' + logger.colors.underline + net.myID)
            logger.info('Our Public key: ' + self.onionrCore._crypto.pubKey)
            time.sleep(1)
            #TODO make runable on windows
            subprocess.Popen([communicatorDaemon, "run", str(net.socksPort)])
            logger.debug('Started communicator')
            events.event('daemon_start', onionr = self)
        self.api = api.API(self.debug)

        return

    def killDaemon(self):
        '''
            Shutdown the Onionr daemon
        '''

        logger.warn('Killing the running daemon...', timestamp = False)
        try:
            events.event('daemon_stop', onionr = self)
            net = NetController(config.get('client.port', 59496))
            try:
                self.onionrCore.daemonQueueAdd('shutdown')
            except sqlite3.OperationalError:
                pass

            net.killTor()
        except Exception as e:
            logger.error('Failed to shutdown daemon.', error = e, timestamp = False)

        return

    def showStats(self):
        '''
            Displays statistics and exits
        '''

        try:
            # define stats messages here
            totalBlocks = len(Block.getBlocks())
            signedBlocks = len(Block.getBlocks(signed = True))
            powToken = self.onionrCore._crypto.pubKeyPowToken
            messages = {
                # info about local client
                'Onionr Daemon Status' : ((logger.colors.fg.green + 'Online') if self.onionrUtils.isCommunicatorRunning(timeout = 2) else logger.colors.fg.red + 'Offline'),
                'Public Key' : self.onionrCore._crypto.pubKey,
                'POW Token' : powToken,
                'Combined' : self.onionrCore._crypto.pubKey + '-' + powToken,
                'Human readable public key' : self.onionrCore._utils.getHumanReadableID(),
                'Node Address' : self.get_hostname(),

                # file and folder size stats
                'div1' : True, # this creates a solid line across the screen, a div
                'Total Block Size' : onionrutils.humanSize(onionrutils.size('data/blocks/')),
                'Total Plugin Size' : onionrutils.humanSize(onionrutils.size('data/plugins/')),
                'Log File Size' : onionrutils.humanSize(onionrutils.size('data/output.log')),

                # count stats
                'div2' : True,
                'Known Peers Count' : str(len(self.onionrCore.listPeers()) - 1),
                'Enabled Plugins Count' : str(len(config.get('plugins.enabled', list()))) + ' / ' + str(len(os.listdir('data/plugins/'))),
                'Known Blocks Count' : str(totalBlocks),
                'Percent Blocks Signed' : str(round(100 * signedBlocks / max(totalBlocks, 1), 2)) + '%'
            }

            # color configuration
            colors = {
                'title' : logger.colors.bold,
                'key' : logger.colors.fg.lightgreen,
                'val' : logger.colors.fg.green,
                'border' : logger.colors.fg.lightblue,

                'reset' : logger.colors.reset
            }

            # pre-processing
            maxlength = 0
            width = self.getConsoleWidth()
            for key, val in messages.items():
                if not (type(val) is bool and val is True):
                    maxlength = max(len(key), maxlength)
            prewidth = maxlength + len(' | ')
            groupsize = width - prewidth - len('[+] ')

            # generate stats table
            logger.info(colors['title'] + 'Onionr v%s Statistics' % ONIONR_VERSION + colors['reset'])
            logger.info(colors['border'] + '-' * (maxlength + 1) + '+' + colors['reset'])
            for key, val in messages.items():
                if not (type(val) is bool and val is True):
                    val = [str(val)[i:i + groupsize] for i in range(0, len(str(val)), groupsize)]

                    logger.info(colors['key'] + str(key).rjust(maxlength) + colors['reset'] + colors['border'] + ' | ' + colors['reset'] + colors['val'] + str(val.pop(0)) + colors['reset'])

                    for value in val:
                        logger.info(' ' * maxlength + colors['border'] + ' | ' + colors['reset'] + colors['val'] + str(value) + colors['reset'])
                else:
                    logger.info(colors['border'] + '-' * (maxlength + 1) + '+' + colors['reset'])
            logger.info(colors['border'] + '-' * (maxlength + 1) + '+' + colors['reset'])
        except Exception as e:
            logger.error('Failed to generate statistics table.', error = e, timestamp = False)

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
                logger.info(logger.colors.bold + command  + logger.colors.reset + logger.colors.fg.blue + ' : ' + logger.colors.reset +  helpmenu[command.lower()], timestamp = False)
            else:
                logger.warn(logger.colors.bold + command  + logger.colors.reset + logger.colors.fg.blue + ' : ' + logger.colors.reset + 'No help menu entry was found', timestamp = False)
        else:
            self.version(0)
            for command, helpmessage in helpmenu.items():
                self.showHelp(command)
        return

    def get_hostname(self):
        try:
            with open('./data/hs/hostname', 'r') as hostname:
                return hostname.read().strip()
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

    def addFile(self):
        '''
            Adds a file to the onionr network
        '''

        if len(sys.argv) >= 3:
            filename = sys.argv[2]
            contents = None

            if not os.path.exists(filename):
                logger.warn('That file does not exist. Improper path?')

            try:
                blockhash = Block.createChain(file = filename)
                logger.info('File %s saved in block %s.' % (filename, blockhash))
            except:
                logger.error('Failed to save file in block.', timestamp = False)
        else:
            logger.error('%s add-file <filename>' % sys.argv[0], timestamp = False)

    def openUI(self):
        import webbrowser
        url = 'http://127.0.0.1:%s/ui/index.html?timingToken=%s' % (config.get('client.port', 59496), self.onionrUtils.getTimeBypassToken())

        print('Opening %s ...' % url)
        webbrowser.open(url, new = 1, autoraise = True)

if __name__ == "__main__":
    Onionr()
