'''
    Onionr - Private P2P Communication

    Open the web interface properly into a web browser
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
import webbrowser
import logger
from onionrutils import getclientapiserver
import config

def get_url():
    try:
        url = getclientapiserver.get_client_API_server()
    except FileNotFoundError:
        url = ""
        logger.error('Onionr seems to not be running (could not get api host)', terminal=True)
    else:
        url = 'http://%s/#%s' % (url, config.get('client.webpassword'))
        logger.info('Onionr web interface URL: ' + url, terminal=True)
    return url

get_url.onionr_help = "Shows the Onionr web interface URL with API key"

def open_home():
    try:
        url = getclientapiserver.get_client_API_server()
    except FileNotFoundError:
        logger.error('Onionr seems to not be running (could not get api host)', terminal=True)
    else:
        url = 'http://%s/#%s' % (url, config.get('client.webpassword'))
        logger.info('If Onionr does not open automatically, use this URL: ' + url, terminal=True)
        webbrowser.open_new_tab(url)

open_home.onionr_help = "Opens the Onionr web UI in the default browser. Node must be running."
