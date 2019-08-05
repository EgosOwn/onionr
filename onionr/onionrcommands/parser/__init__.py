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

def register_plugin_commands(cmd):
    cmd = 'on_%s_cmd' % (cmd,)
    for pl in onionrplugins.get_enabled_plugins():
        pl = onionrplugins.get_plugin(pl)
        if hasattr(pl, cmd):
            getattr(pl, cmd)(onionrpluginapi.PluginAPI)
            return True

def register():
    try:
        cmd = sys.argv[1]
    except IndexError:
        cmd = ""

    try:
        arguments.get_func(cmd)()
    except onionrexceptions.NotFound:
        if not register_plugin_commands(cmd):
            recommend.recommend()
            sys.exit(3)