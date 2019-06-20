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
def open_home(o_inst):
    try:
        url = o_inst.onionrUtils.getClientAPIServer()
    except FileNotFoundError:
        logger.error('Onionr seems to not be running (could not get api host)', terminal=True)
    else:
        url = 'http://%s/#%s' % (url, o_inst.onionrCore.config.get('client.webpassword'))
        logger.info('If Onionr does not open automatically, use this URL: ' + url, terminal=True)
        webbrowser.open_new_tab(url)