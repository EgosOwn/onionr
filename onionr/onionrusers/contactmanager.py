'''
    Onionr - P2P Anonymous Storage Network

    Sets more abstract information related to a peer. Can be thought of as traditional 'contact' system
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
import os, json
from onionrusers import onionrusers

class ContactManager(onionrusers.OnionrUser):
    def __init__(self, coreInst, publicKey, saveUser=False):
        super(ContactManager, self).__init__(coreInst, publicKey, saveUser=saveUser)
        self.data = {}
        self.dataDir = coreInst.dataDir + '/contacts/'
        self.dataFile = coreInst.dataFile = publicKey + '.json'
        if not os.path.exists(self.dataFile):
            os.mkdir(self.dataDir)
    
    def _writeData(self):
        data = json.dumps(self.data)
        with open(self.dataFile, 'w') as dataFile:
            dataFile.write(data)

    def set_info(self, key, value):
        return
    def add_contact(self):
        return
    def delete_contact(self):
        return
    