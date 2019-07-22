'''
    Onionr - Private P2P Communication

    Load the user's inbox and return it as a list
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
import onionrblockapi
def load_inbox(myCore):
    inbox_list = []
    deleted = myCore.keyStore.get('deleted_mail')
    if deleted is None:
        deleted = []

    for blockHash in myCore.getBlocksByType('pm'):
        block = onionrblockapi.Block(blockHash, core=myCore)
        block.decrypt()
        if block.decrypted and blockHash not in deleted:
            inbox_list.append(blockHash)
    return inbox_list