"""Onionr - Private P2P Communication.

Toggle the bootstrap configuration
"""
import sys

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


def toggle_bootstrap_config():
    """Toggles the bootstrap configuration."""
    if config.get('general.use_bootstrap_list') is None:
        logger.error('No general.bootstrap_list setting found')
        sys.exit(3)
    flipped: bool = not config.get('general.use_bootstrap_list')
    config.set('general.use_bootstrap_list', flipped, savefile=True)
