"""Onionr - Private P2P Communication.

Reset default plugins from source
"""
import os
import shutil

from utils import identifyhome
import logger
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


def reset():
    """Reinstalls Onionr default plugins."""
    home = identifyhome.identify_home()
    plugin_dir = home + '/plugins/'
    if not os.path.exists(home):
        return
    if os.path.exists(plugin_dir):
        shutil.rmtree(plugin_dir)

    logger.info('Default plugins have been reset.', terminal=True)


reset.onionr_help = "reinstalls default Onionr plugins"  # type: ignore
reset.onionr_help += "(e.g. mail). Should be done after "  # type: ignore
reset.onionr_help += "git pulls or plugin modification."  # type: ignore
