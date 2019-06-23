'''
    Onionr - Private P2P Communication

    This module defines commands for CLI usage
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

import webbrowser, sys
import logger
from . import pubkeymanager, onionrstatistics, daemonlaunch, filecommands, plugincommands, keyadders
from . import banblocks, exportblocks, openwebinterface, resettor
from onionrutils import importnewblocks

def show_help(o_inst, command):

    helpmenu = o_inst.getHelp()

    if command is None and len(sys.argv) >= 3:
        for cmd in sys.argv[2:]:
            o_inst.showHelp(cmd)
    elif not command is None:
        if command.lower() in helpmenu:
            logger.info(logger.colors.bold + command  + logger.colors.reset + logger.colors.fg.blue + ' : ' + logger.colors.reset +  helpmenu[command.lower()], timestamp = False)
        else:
            logger.warn(logger.colors.bold + command  + logger.colors.reset + logger.colors.fg.blue + ' : ' + logger.colors.reset + 'No help menu entry was found', timestamp = False)
    else:
        o_inst.version(0)
        for command, helpmessage in helpmenu.items():
            o_inst.showHelp(command)

def get_commands(onionr_inst):
    return {'': onionr_inst.showHelpSuggestion,
    'help': onionr_inst.showHelp,
    'version': onionr_inst.version,
    'header': onionr_inst.cmdHeader,
    'config': onionr_inst.configure,
    'start': onionr_inst.start,
    'stop': onionr_inst.killDaemon,
    'status': onionr_inst.showStats,
    'statistics': onionr_inst.showStats,
    'stats': onionr_inst.showStats,
    'details' : onionr_inst.showDetails,
    'detail' : onionr_inst.showDetails,
    'show-details' : onionr_inst.showDetails,
    'show-detail' : onionr_inst.showDetails,
    'showdetails' : onionr_inst.showDetails,
    'showdetail' : onionr_inst.showDetails,
    'get-details' : onionr_inst.showDetails,
    'get-detail' : onionr_inst.showDetails,
    'getdetails' : onionr_inst.showDetails,
    'getdetail' : onionr_inst.showDetails,

    'enable-plugin': onionr_inst.enablePlugin,
    'enplugin': onionr_inst.enablePlugin,
    'enableplugin': onionr_inst.enablePlugin,
    'enmod': onionr_inst.enablePlugin,
    'disable-plugin': onionr_inst.disablePlugin,
    'displugin': onionr_inst.disablePlugin,
    'disableplugin': onionr_inst.disablePlugin,
    'dismod': onionr_inst.disablePlugin,
    'reload-plugin': onionr_inst.reloadPlugin,
    'reloadplugin': onionr_inst.reloadPlugin,
    'reload-plugins': onionr_inst.reloadPlugin,
    'reloadplugins': onionr_inst.reloadPlugin,
    'create-plugin': onionr_inst.createPlugin,
    'createplugin': onionr_inst.createPlugin,
    'plugin-create': onionr_inst.createPlugin,

    'listkeys': onionr_inst.listKeys,
    'list-keys': onionr_inst.listKeys,

    'addpeer': onionr_inst.addPeer,
    'add-peer': onionr_inst.addPeer,
    'add-address': onionr_inst.addAddress,
    'add-addr': onionr_inst.addAddress,
    'addaddr': onionr_inst.addAddress,
    'addaddress': onionr_inst.addAddress,
    'list-peers': onionr_inst.listPeers,

    'blacklist-block': onionr_inst.banBlock,

    'add-file': onionr_inst.addFile,
    'addfile': onionr_inst.addFile,
    'addhtml': onionr_inst.addWebpage,
    'add-html': onionr_inst.addWebpage,
    'add-site': onionr_inst.addWebpage,
    'addsite': onionr_inst.addWebpage,

    'openhome': onionr_inst.openHome,
    'open-home': onionr_inst.openHome,

    'export-block': onionr_inst.exportBlock,
    'exportblock': onionr_inst.exportBlock,

    'get-file': onionr_inst.getFile,
    'getfile': onionr_inst.getFile,

    'listconn': onionr_inst.listConn,
    'list-conn': onionr_inst.listConn,

    'import-blocks': importnewblocks.import_new_blocks,
    'importblocks': importnewblocks.import_new_blocks,

    'introduce': onionr_inst.onionrCore.introduceNode,
    'pex': onionr_inst.doPEX,

    'getpassword': onionr_inst.printWebPassword,
    'get-password': onionr_inst.printWebPassword,
    'getpwd': onionr_inst.printWebPassword,
    'get-pwd': onionr_inst.printWebPassword,
    'getpass': onionr_inst.printWebPassword,
    'get-pass': onionr_inst.printWebPassword,
    'getpasswd': onionr_inst.printWebPassword,
    'get-passwd': onionr_inst.printWebPassword,

    'friend': onionr_inst.friendCmd,
    'addid': onionr_inst.addID,
    'add-id': onionr_inst.addID,
    'change-id': onionr_inst.changeID,

    'reset-tor': resettor.reset_tor
    }

cmd_help = {
    'help': 'Displays this Onionr help menu',
    'version': 'Displays the Onionr version',
    'config': 'Configures something and adds it to the file',

    'start': 'Starts the Onionr daemon',
    'stop': 'Stops the Onionr daemon',

    'stats': 'Displays node statistics',
    'details': 'Displays the web password, public key, and human readable public key',

    'enable-plugin': 'Enables and starts a plugin',
    'disable-plugin': 'Disables and stops a plugin',
    'reload-plugin': 'Reloads a plugin',
    'create-plugin': 'Creates directory structure for a plugin',

    'add-peer': 'Adds a peer to database',
    'list-peers': 'Displays a list of peers',
    'add-file': 'Create an Onionr block from a file',
    'get-file': 'Get a file from Onionr blocks',
    'import-blocks': 'import blocks from the disk (Onionr is transport-agnostic!)',
    'listconn': 'list connected peers',
    'pex': 'exchange addresses with peers (done automatically)',
    'blacklist-block': 'deletes a block by hash and permanently removes it from your node',
    'introduce': 'Introduce your node to the public Onionr network',
    'friend': '[add|remove] [public key/id]',
    'add-id': 'Generate a new ID (key pair)',
    'change-id': 'Change active ID',
    'open-home': 'Open your node\'s home/info screen',
    'reset-tor': 'Delete the Tor data directory. Only do this if Tor never starts.'
        }
