"""Onionr - Private P2P Communication.

Add bridge info to torrc configuration string
"""
import config
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


def add_bridges(torrc: str) -> str:
    """Configure tor to use a bridge using Onionr config keys."""
    config.reload()
    if config.get('tor.use_bridge', False) is True:
        bridge = config.get('tor.bridge_ip', None)
        if bridge is not None:
            # allow blank fingerprint purposefully
            fingerprint = config.get('tor.bridge_fingerprint', '')
            torrc += '\nUseBridges 1\nBridge %s %s\n' % (bridge, fingerprint)
        if not bridge:
            logger.error('Bridge was enabled but not specified in config, ' +
                         'this probably won\'t work', terminal=True)

    return torrc
