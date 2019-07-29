'''
    Onionr - Private P2P Communication

    This default plugin handles private messages in an email like fashion
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
import logger, config, threading, time, datetime
from onionrblockapi import Block
import onionrexceptions
from onionrusers import onionrusers
from utils import reconstructhash
from onionrutils import stringvalidators, escapeansi, bytesconverter
import locale, sys, os, json

locale.setlocale(locale.LC_ALL, '')

plugin_name = 'pms'
PLUGIN_VERSION = '0.0.1'

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import sentboxdb, mailapi, loadinbox # import after path insert
flask_blueprint = mailapi.flask_blueprint

def add_deleted(keyStore, bHash):
    existing = keyStore.get('deleted_mail')
    bHash = reconstructhash.reconstruct_hash(bHash)
    if existing is None:
        existing = []
    else:
        if bHash in existing:
            return
    keyStore.put('deleted_mail', existing.append(bHash))

def on_insertblock(api, data={}):
    meta = json.loads(data['meta'])
    if meta['type'] == 'pm':
        sentboxTools = sentboxdb.SentBox()
        sentboxTools.addToSent(data['hash'], data['peer'], data['content'], meta['subject'])

def on_init(api, data = None):
    '''
        This event is called after Onionr is initialized, but before the command
        inputted is executed. Could be called when daemon is starting or when
        just the client is running.
    '''

    pluginapi = api

    return
