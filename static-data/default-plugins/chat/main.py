'''
    Onionr - Private P2P Communication

    Instant message conversations with Onionr peers
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

# Imports some useful libraries
import locale, sys, os, threading, ujson as json
locale.setlocale(locale.LC_ALL, '')
import onionrservices, logger, config
from onionrservices import bootstrapservice
from onionrutils import stringvalidators, epoch, basicrequests

plugin_name = 'chat'
PLUGIN_VERSION = '0.0.0'
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import controlapi, peerserver
flask_blueprint = controlapi.flask_blueprint
direct_blueprint = peerserver.direct_blueprint
security_whitelist = ['staticfiles.chat', 'staticfiles.chatIndex']

def exit_with_error(text=''):
    if text != '':
        logger.error(text)
    sys.exit(1)
