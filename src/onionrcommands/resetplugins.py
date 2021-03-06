'''
    Onionr - Private P2P Communication

    Reset default plugins from source
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
import os
import shutil

from utils import identifyhome
from onionrsetup import setup_default_plugins
import logger

def reset():
    """Reinstalls Onionr default plugins"""
    home = identifyhome.identify_home()
    plugin_dir = home + '/plugins/'
    if not os.path.exists(home): return
    if os.path.exists(plugin_dir): shutil.rmtree(plugin_dir)

    logger.info('Default plugins have been reset.', terminal=True)

reset.onionr_help = "reinstalls default Onionr plugins (e.g. mail). Should be done after git pulls or plugin modification."
