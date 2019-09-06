'''
    Onionr - Private P2P Communication

    This module loads in the Onionr arguments and their help messages
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
import logger, onionrexceptions
import onionrplugins
import onionrpluginapi
from . import arguments, recommend

plugin_command = lambda cmd: 'on_%s_cmd' % (cmd,)

def register_plugin_commands(cmd):
    plugin_cmd = plugin_command(cmd)
    for pl in onionrplugins.get_enabled_plugins():
        pl = onionrplugins.get_plugin(pl)
        if hasattr(pl, plugin_cmd):
            getattr(pl, plugin_cmd)(onionrpluginapi.PluginAPI)
            return True
    return False

def register():
    """Registers commands and handles help command processing"""
    def get_help_message(cmd: str, default: str = 'No help available for this command'):
        """Return help message for a given command, supports plugin commands"""
        pl_cmd = plugin_command(cmd)
        for pl in onionrplugins.get_enabled_plugins():
            pl = onionrplugins.get_plugin(pl)
            if hasattr(pl, pl_cmd):
                try:
                    return getattr(pl, pl_cmd).onionr_help
                except AttributeError:
                    pass
        
        for i in arguments.get_arguments():
            for alias in i:
                try:
                    return arguments.get_help(cmd)
                except AttributeError:
                    pass
        return default # Return the help string

    PROGRAM_NAME = "onionr"

    # Get the command
    try:
        cmd = sys.argv[1]
    except IndexError:
        logger.debug("Detected Onionr run with no commands specified")
        return

    is_help_cmd = False
    if cmd.replace('--', '').lower() == 'help': is_help_cmd = True

    try:
        arguments.get_func(cmd)()
    except onionrexceptions.NotFound:
        if not register_plugin_commands(cmd) and not is_help_cmd:
            recommend.recommend()
            sys.exit(3)
    
    if is_help_cmd:
        try:
            sys.argv[2]
        except IndexError:
            for i in arguments.get_arguments():
                logger.info('%s <%s>: %s' % (PROGRAM_NAME, '/'.join(i), get_help_message(i[0])), terminal=True)
            for pl in onionrplugins.get_enabled_plugins():
                pl = onionrplugins.get_plugin(pl)
                if hasattr(pl, 'ONIONR_COMMANDS'):
                    print('')
                    try:
                        logger.info('%s commands:' % (pl.plugin_name,), terminal=True)
                    except AttributeError:
                        logger.info('%s commands:' % (pl.__name__,), terminal=True)
                    for plugin_cmd in pl.ONIONR_COMMANDS:
                        logger.info('%s %s: %s' % (PROGRAM_NAME, plugin_cmd, get_help_message(plugin_cmd)), terminal=True)
                    print('')
        else:
            try:
                logger.info('%s %s: %s' % (PROGRAM_NAME, sys.argv[2], get_help_message(sys.argv[2])), terminal=True)
            except KeyError:
                logger.error('%s: command does not exist.' % [sys.argv[2]], terminal=True)
                sys.exit(3)
        return
    