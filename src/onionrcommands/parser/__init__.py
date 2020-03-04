"""Onionr - Private P2P Communication.

This module loads in the Onionr arguments and their help messages
"""
import sys
import os

try:
    if sys.argv[1] not in ('start', 'details', 'show-details'):
        os.chdir(os.environ['ORIG_ONIONR_RUN_DIR'])
except (KeyError, IndexError) as _:
    pass

import logger
import onionrexceptions
import onionrplugins
from onionrplugins import onionrpluginapi
from . import arguments, recommend
"""
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
"""


def plugin_command(cmd):
    """Build a plugin command function name."""
    return f'on_{cmd}_cmd'


def register_plugin_commands(cmd) -> bool:
    """Find a plugin command hook and execute it for a given cmd."""
    plugin_cmd = plugin_command(cmd)
    for pl in onionrplugins.get_enabled_plugins():
        pl = onionrplugins.get_plugin(pl)
        if hasattr(pl, plugin_cmd):
            getattr(pl, plugin_cmd)(onionrpluginapi.PluginAPI)
            return True
    return False


def _show_term(msg: str):
    logger.info(msg, terminal=True)


def register():
    """Register commands and handles help command processing."""
    def get_help_message(cmd: str,
                         default: str = 'No help available for this command'):
        """Print help message for a given command, supports plugin commands."""
        pl_cmd = plugin_command(cmd)
        for pl in onionrplugins.get_enabled_plugins():
            pl = onionrplugins.get_plugin(pl)
            if hasattr(pl, pl_cmd):
                try:
                    return getattr(pl, pl_cmd).onionr_help
                except AttributeError:
                    pass

        for i in arguments.get_arguments():
            for _ in i:
                try:
                    return arguments.get_help(cmd)
                except AttributeError:
                    pass
        return default  # Return the help string

    PROGRAM_NAME = "onionr"

    # Get the command
    try:
        cmd = sys.argv[1]
    except IndexError:
        logger.info('Run with --help to see available commands', terminal=True)
        sys.exit(10)

    is_help_cmd = False
    if cmd.replace('--', '').lower() == 'help':
        is_help_cmd = True

    try:
        try:
            arguments.get_func(cmd)()
        except KeyboardInterrupt:
            pass
    except onionrexceptions.NotFound:
        if not register_plugin_commands(cmd) and not is_help_cmd:
            recommend.recommend()
            sys.exit(3)

    if is_help_cmd:
        try:
            sys.argv[2]
        except IndexError:
            for i in arguments.get_arguments():
                _show_term('%s <%s>: %s' % (PROGRAM_NAME, '/'.join(i),
                                            get_help_message(i[0])))
            for pl in onionrplugins.get_enabled_plugins():
                pl = onionrplugins.get_plugin(pl)
                if hasattr(pl, 'ONIONR_COMMANDS'):
                    print('')
                    try:
                        _show_term('%s commands:' % (pl.plugin_name,))
                    except AttributeError:
                        _show_term('%s commands:' % (pl.__name__,))
                    for plugin_cmd in pl.ONIONR_COMMANDS:
                        _show_term('%s %s: %s' %
                                   (PROGRAM_NAME,
                                    plugin_cmd,
                                    get_help_message(plugin_cmd)),)
                    print('')
        else:
            try:
                _show_term('%s %s: %s' % (PROGRAM_NAME,
                                          sys.argv[2],
                                          get_help_message(sys.argv[2])))
            except KeyError:
                logger.error('%s: command does not exist.' % [sys.argv[2]],
                             terminal=True)
                sys.exit(3)
        return
