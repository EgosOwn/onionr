"""Onionr - Private P2P Communication.

Open the web interface properly into a web browser
"""
import webbrowser
from time import sleep

import logger
from onionrutils import getclientapiserver
import config
from onionrutils.localcommand import local_command

from .daemonlaunch import geturl
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


def _tell_if_ui_not_ready():
    if local_command('/torready') != 'true':
        logger.warn('The UI is not ready yet, waiting on Tor to start.', terminal=True)


def _wait_for_ui_to_be_ready():
    if config.get('general.offline_mode', False) or \
        not config.get('transports.tor', True) or \
            config.get('tor.use_existing_tor'):
        return
    _tell_if_ui_not_ready()
    while local_command('/torready') != 'true':
        sleep(0.5)
    logger.info("Tor is ready, opening UI", terminal=True)


def get_url() -> str:
    """Build UI URL string and return it."""
    return geturl.get_url(config)


get_url.onionr_help = "Shows the Onionr "  # type: ignore
get_url.onionr_help += "web interface URL with API key"  # type: ignore


def open_home():
    """Command to open web interface URL in default browser."""
    try:
        url = getclientapiserver.get_client_API_server()
    except FileNotFoundError:
        logger.error(
            'Onionr seems to not be running (could not get api host)',
            terminal=True)
    else:
        _wait_for_ui_to_be_ready()  # wait for Tor/transports to start
        sleep(3)  # Sleep a little longer to wait for web UI to init some vars it needs
        url = get_url()
        logger.info(
            'If Onionr does not open automatically, use this URL: ' + url,
            terminal=True)
        webbrowser.open_new_tab(url)


open_home.onionr_help = "Opens the Onionr UI in the default "  # type: ignore
open_home.onionr_help += "browser. Node must be running."  # type: ignore
