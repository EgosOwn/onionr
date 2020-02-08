"""
    Onionr - Private P2P Communication

    Installs default plugins
"""
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
import os, shutil

import onionrplugins as plugins
import logger
import filepaths
from utils.readstatic import get_static_dir

def setup_default_plugins():
    # Copy default plugins into plugins folder
    if not os.path.exists(plugins.get_plugins_folder()):
        if os.path.exists(get_static_dir() + '/default-plugins/'):
            names = [f for f in os.listdir(get_static_dir() + '/default-plugins/')]
            try:
                shutil.copytree(
                    get_static_dir() + '/default-plugins/',
                    plugins.get_plugins_folder())
            except FileExistsError:
                pass

            # Enable plugins
            for name in names:
                if not name in plugins.get_enabled_plugins():
                    plugins.enable(name)

    for name in plugins.get_enabled_plugins():
        if not os.path.exists(plugins.get_plugin_data_folder(name)):
            try:
                os.mkdir(plugins.get_plugin_data_folder(name))
            except FileExistsError:
                pass
            except Exception as e:
                #logger.warn('Error enabling plugin: ' + str(e), terminal=True)
                plugins.disable(name, stop_event = False)
