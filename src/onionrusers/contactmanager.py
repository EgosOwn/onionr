"""Onionr - Private P2P Communication.

Set more abstract information related to a peer.
Can be thought of as traditional 'contact' system
"""
import os

import ujson as json
import unpaddedbase32

import onionrexceptions
from onionrusers import onionrusers
from onionrutils import bytesconverter, epoch
from utils import identifyhome
from onionrutils import mnemonickeys
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


class ContactManager(onionrusers.OnionrUser):
    def __init__(self, publicKey, saveUser=False, recordExpireSeconds=5):
        try:
            if mnemonickeys.DELIMITER in publicKey:
                publicKey = mnemonickeys.get_base32(publicKey)
                #publicKey = unpaddedbase32.b32encode(bytesconverter.str_to_bytes(publicKey))
        except ValueError:
            pass
        publicKey = bytesconverter.bytes_to_str(unpaddedbase32.repad(bytesconverter.str_to_bytes(publicKey)))
        super(ContactManager, self).__init__(publicKey, saveUser=saveUser)
        home = identifyhome.identify_home()
        self.dataDir = home + '/contacts/'
        self.dataFile = '%s/contacts/%s.json' % (home, publicKey)
        self.lastRead = 0
        self.recordExpire = recordExpireSeconds
        self.data = self._loadData()
        self.deleted = False

        if not os.path.exists(self.dataDir):
            os.mkdir(self.dataDir)

    def _writeData(self):
        data = json.dumps(self.data)
        with open(self.dataFile, 'w') as dataFile:
            dataFile.write(data)

    def _loadData(self):
        self.lastRead = epoch.get_epoch()
        retData = {}
        if os.path.exists(self.dataFile):
            with open(self.dataFile, 'r') as dataFile:
                retData = json.loads(dataFile.read())
        return retData

    def set_info(self, key, value, autoWrite=True):
        if self.deleted:
            raise onionrexceptions.ContactDeleted

        self.data[key] = value
        if autoWrite:
            self._writeData()
        return

    def get_info(self, key, forceReload=False):
        if self.deleted:
            raise onionrexceptions.ContactDeleted

        if (epoch.get_epoch() - self.lastRead >= self.recordExpire) or forceReload:
            self.data = self._loadData()
        try:
            return self.data[key]
        except KeyError:
            return None

    def delete_contact(self):
        self.deleted = True
        if os.path.exists(self.dataFile):
            os.remove(self.dataFile)