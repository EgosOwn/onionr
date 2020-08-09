"""Onionr - P2P Anonymous Storage Network.

Return stem Tor controller instance
"""
from stem.control import Controller

import config
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
config.reload()


def get_controller() -> Controller:
    """Create and return a Tor controller connection."""
    port = config.get('tor.controlPort', 0)
    password = config.get('tor.controlpassword', '')
    if config.get('tor.use_existing_tor', False):
        port = config.get('tor.existing_control_port', 0)
        password = config.get('tor.existing_control_password', '')
    c = Controller.from_port(port=port)
    c.authenticate(password)
    return c
