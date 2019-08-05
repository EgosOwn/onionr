from .. import onionrstatistics, version, daemonlaunch, keyadders, openwebinterface
from .. import banblocks # Command to blacklist a block by its hash
from .. import filecommands # commands to share files with onionr
from .. import exportblocks # commands to export blocks
from .. import pubkeymanager # commands to add or change id
from .. import resettor # command to reset the tor data directory
import onionrexceptions
from onionrutils import importnewblocks # func to import new blocks
import onionrevents as events
def get_arguments():
    '''This is a function because we need to be able to dynamically modify them with plugins'''
    args = {
        ('blacklist', 'blacklist-block', 'remove-block', 'removeblock'): banblocks.ban_block,
        ('details', 'info'): onionrstatistics.show_details,
        ('stats', 'statistics'): onionrstatistics.show_stats,
        ('version'): version.version,
        ('start', 'daemon'): daemonlaunch.start,
        ('stop', 'kill'): daemonlaunch.kill_daemon,
        ('add-address', 'addaddress', 'addadder'): keyadders.add_address,
        ('openhome', 'gui', 'openweb', 'open-home', 'open-web'): openwebinterface.open_home,
        ('add-site', 'addsite', 'addhtml', 'add-html'): filecommands.add_html,
        ('addfile', 'add-file'): filecommands.add_file,
        ('get-file', 'getfile'): filecommands.get_file,
        ('export-block', 'exportblock'): exportblocks.export_block,
        ('importblocks', 'import-blocks'): importnewblocks.import_new_blocks,
        ('addid', 'add-id'): pubkeymanager.add_ID,
        ('changeid', 'change-id'): pubkeymanager.change_ID,
        ('resettor', 'reset-tor'): resettor.reset_tor

    }
    return args

def get_help():
    return

def get_func(argument):
    argument = argument.lower()
    args = get_arguments()

    for arg in args.keys(): # Iterate command alias sets
        if argument in arg: # If our argument is in the current alias set, return the command function
            return args[arg]
    raise onionrexceptions.NotFound