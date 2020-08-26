"""Onionr - Private P2P Communication.

Load web UI client endpoints into the whitelist from plugins
"""
import onionrplugins
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


def load_plugin_security_whitelist_endpoints(whitelist: list):
    """Accept a list reference of whitelist endpoints from security/client.py and
    append plugin's specified endpoints to them by attribute"""
    for plugin in onionrplugins.get_enabled_plugins():
        try:
            plugin = onionrplugins.get_plugin(plugin)
        except FileNotFoundError:
            continue
        try:
            whitelist.extend(getattr(plugin, "security_whitelist"))
        except AttributeError:
            pass
