"""Onionr - Private P2P Communication.

Private messages in an email like fashion
"""
import locale
import sys
import os

import ujson as json

from onionrusers import contactmanager
from utils import reconstructhash
from onionrutils import bytesconverter
import config
import notifier
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

locale.setlocale(locale.LC_ALL, '')

plugin_name = 'pms'
PLUGIN_VERSION = '0.1.2'

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import sentboxdb, mailapi, loadinbox # import after path insert
from onblacklist import on_blacklist_add

flask_blueprint = mailapi.flask_blueprint
security_whitelist = ['mail.mailstatic', 'mail.mailindex']


def add_deleted(keyStore, b_hash):
    existing = keyStore.get('deleted_mail')
    bHash = reconstructhash.reconstruct_hash(b_hash)
    if existing is None:
        existing = []
    else:
        if bHash in existing:
            return
    keyStore.put('deleted_mail', existing.append(b_hash))


def on_insertblock(api, data={}):
    meta = json.loads(data['meta'])
    if meta['type'] == 'pm':
        sentboxTools = sentboxdb.SentBox()
        sentboxTools.addToSent(data['hash'], data['peer'], data['content'], meta['subject'])


def on_processblocks(api, data=None):
    if data['type'] != 'pm':
        return
    notification_func = notifier.notify
    data['block'].decrypt()
    metadata = data['block'].bmetadata

    signer = bytesconverter.bytes_to_str(data['block'].signer)
    user = contactmanager.ContactManager(signer, saveUser=False)
    name = user.get_info("name")
    if name != 'anonymous' and name != None:
        signer = name.title()
    else:
        signer = signer[:5]


    if data['block'].decrypted:
        config.reload()

        if config.get('mail.notificationSound', True):
            notification_func = notifier.notification_with_sound
        if config.get('mail.notificationSetting', True):
            if not config.get('mail.strangersNotification', True):
                if not user.isFriend():
                    return
            notification_func(title="Onionr Mail - New Message", message="From: %s\n\nSubject: %s" % (signer, metadata['subject']))
