'''
    Onionr - Private P2P Communication

    Sets CLI arguments for Onionr
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
from .. import onionrstatistics, version, daemonlaunch, keyadders, openwebinterface
from .. import banblocks # Command to blacklist a block by its hash
from .. import filecommands # commands to share files with onionr
from .. import exportblocks # commands to export blocks
from .. import pubkeymanager # commands to add or change id
from .. import resettor # command to reset the tor data directory
from .. import resetplugins # command to reinstall default plugins
import onionrexceptions
from onionrutils import importnewblocks # func to import new blocks
import onionrevents as events
def get_arguments():
    """This is a function because we need to be able to dynamically modify them with plugins"""
    args = {
        ('blacklist', 'blacklist-block', 'remove-block', 'removeblock', 'banblock', 'ban-block'): banblocks.ban_block,
        ('details', 'info'): onionrstatistics.show_details,
        ('stats', 'statistics'): onionrstatistics.show_stats,
        ('version',): version.version,
        ('start', 'daemon'): daemonlaunch.start,
        ('stop', 'kill'): daemonlaunch.kill_daemon,
        ('add-address', 'addaddress', 'addadder'): keyadders.add_address,
        ('openhome', 'gui', 'openweb', 'open-home', 'open-web'): openwebinterface.open_home,
        ('add-site', 'addsite', 'addhtml', 'add-html'): filecommands.add_html,
        ('addfile', 'add-file'): filecommands.add_file,
        ('get-file', 'getfile'): filecommands.get_file,
        ('export-block', 'exportblock'): exportblocks.export_block,
        ('importblocks', 'import-blocks', 'import-block'): importnewblocks.import_new_blocks,
        ('addid', 'add-id'): pubkeymanager.add_ID,
        ('changeid', 'change-id'): pubkeymanager.change_ID,
        ('resettor', 'reset-tor'): resettor.reset_tor,
        ('resetplugins', 'reset-plugins'): resetplugins.reset

    }
    return args

def get_help(arg: str) -> str:
    """Returns the help info string from a given command"""
    arguments = get_arguments()
    # Iterate the command alias tuples
    for argument in arguments:
        # Return the help message if its found in a command alias tuple
        if arg in argument: return arguments[argument].onionr_help
    raise KeyError

def get_func(argument):
    """Returns the function for a given command argument"""
    argument = argument.lower()
    args = get_arguments()

    for arg in args.keys(): # Iterate command alias sets
        if argument in arg: # If our argument is in the current alias set, return the command function
            return args[arg]
    raise onionrexceptions.NotFound
